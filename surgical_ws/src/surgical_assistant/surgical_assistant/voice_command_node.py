#!/usr/bin/env python3
"""voice_command_node: micrófono → Faster-Whisper (CPU int8) → NLU → /surgical_command.

Hilos:
  * callback de sounddevice  → cola de bloques de audio
  * hilo de segmentación     → detecta inicio/fin de frase por energía (VAD simple)
  * hilo de transcripción    → Whisper + NLU + publicación (para no bloquear la captura)
"""
from __future__ import annotations

import collections
import math
import queue
import threading
import time

import numpy as np
import rclpy
from rclpy.node import Node

from surgical_interfaces.msg import SurgicalCommand
from surgical_assistant.config_loader import load_instruments_config
from surgical_assistant.nlu import INTENT_STOP, INTENT_UNKNOWN, NLU, normalize


class VoiceCommandNode(Node):
    def __init__(self) -> None:
        super().__init__('voice_command_node')

        # --- Parámetros ---------------------------------------------------------------
        self.declare_parameter('whisper_model', 'small')      # tiny | base | small | medium (o ruta local)
        self.declare_parameter('whisper_device', 'cpu')
        self.declare_parameter('whisper_compute_type', 'int8')
        self.declare_parameter('whisper_cpu_threads', 4)
        self.declare_parameter('whisper_beam_size', 1)
        self.declare_parameter('language', 'es')
        self.declare_parameter('audio_device', -1)            # -1 = micrófono por defecto
        self.declare_parameter('sample_rate', 16000)
        self.declare_parameter('block_ms', 30)
        self.declare_parameter('min_rms', 0.01)               # piso absoluto del umbral de voz
        self.declare_parameter('speech_ratio', 3.0)           # umbral = max(min_rms, ruido * ratio)
        self.declare_parameter('start_blocks', 3)             # bloques seguidos sobre umbral para iniciar
        self.declare_parameter('silence_ms', 700)             # silencio que cierra la frase
        self.declare_parameter('min_utterance_s', 0.4)
        self.declare_parameter('max_utterance_s', 6.0)
        self.declare_parameter('preroll_ms', 300)
        self.declare_parameter('instruments_config', '')
        self.declare_parameter('setfit_model_dir', '')        # vacío → reglas por palabras clave
        self.declare_parameter('instrument_threshold', 0.80)
        self.declare_parameter('min_confidence', 0.60)        # 'stop' lo ignora
        self.declare_parameter('require_wake_word', False)
        self.declare_parameter('wake_word', 'asistente')
        self.declare_parameter('command_topic', '/surgical_command')

        p = self.get_parameter
        self.sr = int(p('sample_rate').value)
        self.block = int(self.sr * p('block_ms').value / 1000)
        self.min_rms = float(p('min_rms').value)
        self.speech_ratio = float(p('speech_ratio').value)
        self.start_blocks = int(p('start_blocks').value)
        self.silence_blocks = int(p('silence_ms').value / p('block_ms').value)
        self.min_utt = float(p('min_utterance_s').value)
        self.max_utt = float(p('max_utterance_s').value)
        self.preroll_blocks = int(p('preroll_ms').value / p('block_ms').value)
        self.min_conf = float(p('min_confidence').value)
        self.require_wake = bool(p('require_wake_word').value)
        self.wake_word = normalize(p('wake_word').value)
        self.language = p('language').value
        self.beam = int(p('whisper_beam_size').value)

        # --- NLU ----------------------------------------------------------------------
        cfg = load_instruments_config(p('instruments_config').value)
        self.nlu = NLU(cfg['instruments'], p('setfit_model_dir').value,
                       float(p('instrument_threshold').value), self.get_logger())
        # Sesgo del decodificador hacia el vocabulario quirúrgico (reduce errores en nombres de instrumentos).
        vocab = sorted({a for i in cfg['instruments'].values() for a in i.get('aliases', [])})
        self.initial_prompt = ('Comandos al instrumentista quirúrgico robótico: pásame ' +
                               ', '.join(vocab) + '. Alto. Posición inicial.')

        # --- Whisper ------------------------------------------------------------------
        from faster_whisper import WhisperModel  # import diferido: carga pesada

        self.get_logger().info(f"Cargando Faster-Whisper '{p('whisper_model').value}' "
                               f"({p('whisper_device').value}/{p('whisper_compute_type').value})...")
        self.whisper = WhisperModel(p('whisper_model').value,
                                    device=p('whisper_device').value,
                                    compute_type=p('whisper_compute_type').value,
                                    cpu_threads=int(p('whisper_cpu_threads').value))
        self.get_logger().info('Whisper listo.')

        # --- ROS ----------------------------------------------------------------------
        self.pub = self.create_publisher(SurgicalCommand, p('command_topic').value, 10)

        # --- Hilos --------------------------------------------------------------------
        self._stop = threading.Event()
        self._audio_q: queue.Queue = queue.Queue(maxsize=200)
        self._utt_q: queue.Queue = queue.Queue(maxsize=2)
        self._threads = [
            threading.Thread(target=self._segment_loop, daemon=True),
            threading.Thread(target=self._transcribe_loop, daemon=True),
        ]
        for t in self._threads:
            t.start()
        self._start_stream(int(p('audio_device').value))

    # ------------------------------------------------------------------ audio
    def _start_stream(self, device: int) -> None:
        import sounddevice as sd  # requiere libportaudio2 (apt)

        def callback(indata, frames, time_info, status):  # noqa: ARG001
            if status:
                self.get_logger().warn(f'Audio: {status}', throttle_duration_sec=5.0)
            try:
                self._audio_q.put_nowait(indata[:, 0].copy())
            except queue.Full:
                pass  # preferimos perder audio a bloquear el callback

        self._stream = sd.InputStream(samplerate=self.sr, channels=1, dtype='float32',
                                      blocksize=self.block,
                                      device=None if device < 0 else device,
                                      callback=callback)
        self._stream.start()
        self.get_logger().info('Escuchando micrófono...')

    def _segment_loop(self) -> None:
        preroll = collections.deque(maxlen=self.preroll_blocks)
        noise = self.min_rms
        recording = False
        hot = 0
        silent = 0
        buf: list = []
        while not self._stop.is_set():
            try:
                blk = self._audio_q.get(timeout=0.2)
            except queue.Empty:
                continue
            rms = float(np.sqrt(np.mean(blk ** 2)))
            thr = max(self.min_rms, noise * self.speech_ratio)
            is_speech = rms > thr

            if not recording:
                if not is_speech:
                    noise = 0.95 * noise + 0.05 * rms  # el piso de ruido solo se adapta en silencio
                    hot = 0
                    preroll.append(blk)
                else:
                    hot += 1
                    preroll.append(blk)
                    if hot >= self.start_blocks:
                        recording, silent = True, 0
                        buf = list(preroll)
            else:
                buf.append(blk)
                silent = 0 if is_speech else silent + 1
                dur = len(buf) * self.block / self.sr
                if silent >= self.silence_blocks or dur >= self.max_utt:
                    audio = np.concatenate(buf)
                    recording, hot, buf = False, 0, []
                    preroll.clear()
                    if dur - silent * self.block / self.sr >= self.min_utt:
                        try:
                            self._utt_q.put_nowait(audio)
                        except queue.Full:
                            self.get_logger().warn('Transcriptor ocupado: frase descartada.')

    # ------------------------------------------------------------- transcripción
    def _transcribe_loop(self) -> None:
        while not self._stop.is_set():
            try:
                audio = self._utt_q.get(timeout=0.2)
            except queue.Empty:
                continue
            t0 = time.monotonic()
            try:
                segments, _info = self.whisper.transcribe(
                    audio, language=self.language, beam_size=self.beam,
                    vad_filter=True, condition_on_previous_text=False,
                    initial_prompt=self.initial_prompt, temperature=0.0)
                segments = list(segments)
            except Exception as exc:  # noqa: BLE001
                self.get_logger().error(f'Fallo de transcripción: {exc}')
                continue
            text = ' '.join(s.text.strip() for s in segments).strip()
            if not text:
                continue
            asr_conf = float(np.mean([math.exp(s.avg_logprob) for s in segments]))
            self._handle_text(text, asr_conf, t0)

    def _handle_text(self, text: str, asr_conf: float, t0: float) -> None:
        res = self.nlu.parse(text)
        latency = time.monotonic() - t0
        self.get_logger().info(
            f'[{latency:.2f}s] "{text}" → intent={res.intent} instrument={res.instrument or "-"} '
            f'conf={res.confidence:.2f} asr={asr_conf:.2f}')

        if res.intent == INTENT_UNKNOWN:
            return
        if res.intent != INTENT_STOP:  # 'stop' siempre pasa (seguridad)
            if res.confidence < self.min_conf:
                self.get_logger().warn('Confianza insuficiente: comando ignorado.')
                return
            if self.require_wake and self.wake_word not in normalize(text):
                self.get_logger().info(f'Sin palabra de activación "{self.wake_word}": ignorado.')
                return

        msg = SurgicalCommand()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.intent = res.intent
        msg.instrument_name = res.instrument
        msg.confidence = res.confidence
        msg.asr_confidence = asr_conf
        msg.raw_text = text
        msg.processing_time_s = float(latency)
        self.pub.publish(msg)

    def destroy_node(self) -> bool:
        self._stop.set()
        try:
            self._stream.stop()
            self._stream.close()
        except Exception:  # noqa: BLE001
            pass
        return super().destroy_node()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = VoiceCommandNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
