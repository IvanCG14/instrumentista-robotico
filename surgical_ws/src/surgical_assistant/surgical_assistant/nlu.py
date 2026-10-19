"""NLU del asistente quirúrgico: intención (SetFit o reglas) + instrumento (coincidencia difusa).

Este módulo no depende de ROS, de modo que se puede probar con pytest.
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

INTENT_GIVE = 'give_instrument'
INTENT_RETURN = 'return_instrument'
INTENT_STOP = 'stop'
INTENT_HOME = 'home'
INTENT_UNKNOWN = 'unknown'
INTENTS = [INTENT_GIVE, INTENT_RETURN, INTENT_STOP, INTENT_HOME, INTENT_UNKNOWN]


def normalize(text: str) -> str:
    """Minúsculas, sin tildes ni signos de puntuación, espacios colapsados."""
    text = unicodedata.normalize('NFKD', text.lower())
    text = ''.join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r'[^a-z0-9ñ\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


@dataclass
class NLUResult:
    intent: str
    instrument: str
    confidence: float
    instrument_score: float
    text: str


# ----------------------------------------------------------------------------
# Instrumento
# ----------------------------------------------------------------------------
class InstrumentMatcher:
    """Mapea frases de la transcripción a nombres de clase usando alias + similitud difusa."""

    def __init__(self, instruments_cfg: Dict[str, Dict], threshold: float = 0.80):
        self.threshold = threshold
        self._aliases: List[Tuple[str, str]] = []  # (alias_normalizado, clase)
        for cls, info in instruments_cfg.items():
            names = [cls.replace('_', ' ')] + list(info.get('aliases', []))
            for a in names:
                na = normalize(a)
                if na:
                    self._aliases.append((na, cls))

    def match(self, text: str) -> Tuple[str, float]:
        tokens = normalize(text).split()
        best_cls, best_score, best_len = '', 0.0, 0
        for alias, cls in self._aliases:
            n = len(alias.split())
            if n > len(tokens):
                continue
            for i in range(len(tokens) - n + 1):
                window = ' '.join(tokens[i:i + n])
                score = 1.0 if window == alias else SequenceMatcher(None, window, alias).ratio()
                # Prefiere mayor similitud; a igualdad, el alias más largo ("pinza hemostatica" > "pinza").
                if score > best_score + 1e-9 or (abs(score - best_score) < 1e-9 and len(alias) > best_len):
                    best_cls, best_score, best_len = cls, score, len(alias)
        if best_score >= self.threshold:
            return best_cls, best_score
        return '', 0.0


# ----------------------------------------------------------------------------
# Intención
# ----------------------------------------------------------------------------
_STOP_WORDS = {'alto', 'detente', 'detener', 'stop', 'emergencia', 'cancela', 'cancelar', 'basta'}
_STOP_SHORT_ONLY = {'para', 'parar'}  # ambiguas ("para" = preposición): solo en frases de ≤2 palabras
_HOME_PHRASES = ['posicion inicial', 'posicion de inicio', 'vuelve a casa', 'regresa a casa',
                 've a casa', 've a inicio', 'vuelve a inicio', 'regresa a inicio', 'home', 'descansa']
_RETURN_WORDS = {'toma', 'recibe', 'recibelo', 'devuelvo', 'devuelve', 'guarda', 'recoge',
                 'llevate', 'retira', 'retirar', 'tomalo'}
_GIVE_WORDS = {'pasame', 'pasa', 'dame', 'damelo', 'alcanzame', 'entregame', 'traeme', 'trae',
               'necesito', 'quiero', 'ocupo', 'pasalo', 'alcanza', 'entrega'}


def rule_intent(text: str) -> Tuple[str, float]:
    """Clasificador por palabras clave: devuelve (intención, confianza)."""
    norm = normalize(text)
    tokens = norm.split()
    tset = set(tokens)
    if tset & _STOP_WORDS or (len(tokens) <= 2 and tset & _STOP_SHORT_ONLY):
        return INTENT_STOP, 0.95
    if any(p in norm for p in _HOME_PHRASES):
        return INTENT_HOME, 0.90
    if tset & _RETURN_WORDS:
        return INTENT_RETURN, 0.85
    if tset & _GIVE_WORDS:
        return INTENT_GIVE, 0.85
    return INTENT_UNKNOWN, 0.0


class SetFitIntentClassifier:
    """Envoltorio de un modelo SetFit entrenado con tools/train_intent_setfit.py.

    El directorio del modelo debe contener `labels.json` (lista de intenciones en el orden de
    las clases del modelo).
    """

    def __init__(self, model_dir: str):
        from setfit import SetFitModel  # import diferido: es pesado y opcional

        self.model = SetFitModel.from_pretrained(model_dir)
        with open(os.path.join(model_dir, 'labels.json'), 'r', encoding='utf-8') as f:
            self.labels: List[str] = json.load(f)

    def predict(self, text: str) -> Tuple[str, float]:
        import numpy as np

        probs = self.model.predict_proba([text])
        if hasattr(probs, 'detach'):
            probs = probs.detach().cpu().numpy()
        probs = np.asarray(probs)[0]
        idx = int(probs.argmax())
        return self.labels[idx], float(probs[idx])


class NLU:
    """Combina clasificador de intención + extractor de instrumento.

    Seguridad: la palabra clave de "stop" siempre gana, incluso si SetFit opina otra cosa.
    """

    def __init__(self, instruments_cfg: Dict[str, Dict], setfit_dir: str = '',
                 instrument_threshold: float = 0.80, logger=None):
        self.matcher = InstrumentMatcher(instruments_cfg, instrument_threshold)
        self.setfit: Optional[SetFitIntentClassifier] = None
        if setfit_dir:
            try:
                self.setfit = SetFitIntentClassifier(setfit_dir)
            except Exception as exc:  # noqa: BLE001
                if logger:
                    logger.error(f'No se pudo cargar SetFit en "{setfit_dir}": {exc}. '
                                 'Se usan reglas por palabras clave.')
        elif logger:
            logger.warn('Sin modelo SetFit (parámetro setfit_model_dir vacío): usando reglas por palabras clave.')

    def parse(self, text: str) -> NLUResult:
        rule_i, rule_c = rule_intent(text)
        if rule_i == INTENT_STOP:
            intent, conf = INTENT_STOP, rule_c
        elif self.setfit is not None:
            intent, conf = self.setfit.predict(normalize(text))
        else:
            intent, conf = rule_i, rule_c

        instrument, inst_score = self.matcher.match(text)
        # give/return sin instrumento reconocido no es accionable.
        if intent in (INTENT_GIVE, INTENT_RETURN) and not instrument:
            conf = min(conf, 0.3)
        if intent in (INTENT_STOP, INTENT_HOME):
            instrument = ''
        return NLUResult(intent, instrument, float(conf), float(inst_score), text)
