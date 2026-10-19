#!/usr/bin/env python3
import cv2
import csv
import os
from datetime import datetime

class SurgicalDatasetLogger:
    """
    Logger multitarea para adquisición de datasets quirúrgicos.
    Soporta las 4 fases:
      - F1_Individual: 1 instrumento por toma, ordenado en subcarpeta por ID.
      - F2_Grupos: múltiples instrumentos en escena (solapamiento).
      - F3_Contexto: entorno de quirófano, interacción con manos/bandeja.
      - F4_Variaciones: pruebas de estrés (cambios de luz, ángulos o distancia).
    """
    def __init__(self, metadata, camera_index=0):
        self.meta = metadata
        self.fase_nombre = self.meta['fase_nombre']  # ej. 'F1_Individual'
        self.csv_file = f"{self.fase_nombre}.csv"
        
        # Iniciar cámara con OpenCV
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        # Configuración de rutas
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Estructura de almacenamiento de imágenes
        if self.fase_nombre == 'F1_Individual':
            inst_folder = self.meta['instrument_ids'][0]
            self.img_dir = os.path.join(self.base_dir, 'dataset_bruto', 'imagenes', self.fase_nombre, inst_folder)
        else:
            self.img_dir = os.path.join(self.base_dir, 'dataset_bruto', 'imagenes', self.fase_nombre)
            
        os.makedirs(self.img_dir, exist_ok=True)
        
        self.setup_csv()
        self.capture_counter = self.get_last_capture_id()
        print(f"\n[OK] Sistema listo. Guardando registros en: '{self.csv_file}'")
        print(f"[OK] Las imágenes se guardarán en: '{self.img_dir}'")
        print(f"[OK] Próxima captura asignada: #{self.capture_counter:04d}\n")

    def setup_csv(self):
        """Asegura que el CSV de la fase exista y tenga los encabezados correctos."""
        headers = [
            'capture_id', 'session_id', 'setup_id', 'fecha', 'archivo_imagen', 
            'archivo_profundidad', 'instrument_id', 'nombre_instrumento', 'clase', 
            'distancia_cm', 'formato_imagen', 'iluminacion_id', 'reflejos', 
            'desenfoque', 'mano_presente', 'mano_interactua_con_instrumento', 
            'split', 'estado_revision', 'ruta_anotaciones'
        ]
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)

    def get_last_capture_id(self):
        """Calcula el siguiente número secuencial para no sobrescribir registros."""
        if not os.path.exists(self.csv_file):
            return 1
        with open(self.csv_file, mode='r', encoding='utf-8') as f:
            reader = list(csv.reader(f))
            if len(reader) > 1:
                return len(reader)
        return 1

    def run(self):
        """Bucle principal de previsualización con HUD OpenCV."""
        if not self.cap.isOpened():
            print("[ERROR] No se pudo acceder a la cámara. Verifica la conexión o el índice de cámara.")
            return

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("[ERROR] Fallo al capturar cuadro de video.")
                break

            display_img = frame.copy()
            
            # HUD Dinámico en pantalla
            ids_str = ";".join(self.meta['instrument_ids'])
            hud_text = [
                f"FASE: {self.fase_nombre} | Sesion: {self.meta['session_id']}",
                f"IDs Instrumental: {ids_str}",
                f"Distancia: {self.meta['distancia_cm']} cm | Split: {self.meta['split']}",
                "['S'] Guardar Captura  |  ['Q'] Salir"
            ]
            
            # Fondo oscuro para legibilidad del HUD
            cv2.rectangle(display_img, (5, 5), (600, 130), (0, 0, 0), -1)
            
            y0, dy = 30, 25
            for i, line in enumerate(hud_text):
                color = (0, 255, 0) if i < 3 else (0, 255, 255)
                cv2.putText(display_img, line, (15, y0 + i * dy), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

            h, w = display_img.shape[:2]
            if w > 1280:
                display_img = cv2.resize(display_img, (1280, int(h * 1280 / w)))

            cv2.imshow(f"Surgical Dataset Logger - {self.fase_nombre}", display_img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s') or key == ord('S'):
                self.save_capture(frame)
            elif key == ord('q') or key == ord('Q') or key == 27:
                print("\n[INFO] Cerrando sesión de captura...")
                break
                
        self.cap.release()
        cv2.destroyAllWindows()

    def save_capture(self, image):
        """Guarda la imagen jpg y añade la fila de metadatos al CSV correspondiente."""
        prefix_fase = self.fase_nombre.split('_')[0]  # 'F1', 'F2', 'F3', 'F4'
        
        if self.fase_nombre == 'F1_Individual':
            inst_id = self.meta['instrument_ids'][0]
            capture_id = f"{prefix_fase}_{self.meta['session_id']}_{inst_id}_{self.capture_counter:04d}"
        else:
            capture_id = f"{prefix_fase}_{self.meta['session_id']}_{self.capture_counter:04d}"
            
        filename = f"{capture_id}.jpg"
        filepath = os.path.join(self.img_dir, filename)
        
        # 1. Guardar archivo físico de imagen
        cv2.imwrite(filepath, image)
        
        # 2. Formatear campos para el CSV
        fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        inst_ids_join = ";".join(self.meta['instrument_ids'])
        nombres_join = ";".join(self.meta['nombres'])
        clases_join = ";".join(self.meta['clases'])
        
        row = [
            capture_id, 
            self.meta['session_id'], 
            self.meta['setup_id'], 
            fecha_str, 
            filename, 
            "N/A",  # Mapa de profundidad
            inst_ids_join, 
            nombres_join, 
            clases_join, 
            self.meta['distancia_cm'], 
            "jpg", 
            self.meta['iluminacion_id'], 
            self.meta.get('reflejos', 'Ninguno'), 
            self.meta.get('desenfoque', 'No'), 
            self.meta['mano_presente'], 
            self.meta.get('mano_interactua', 'N/A'), 
            self.meta['split'], 
            "Pendiente", 
            ""  # Ruta de anotaciones
        ]
        
        # 3. Inserción garantizada en disco
        try:
            with open(self.csv_file, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
                f.flush()
                os.fsync(f.fileno())
                
            print(f"[CAPTURADO #{self.capture_counter:04d}] {filename} -> Guardado en {self.csv_file}")
            self.capture_counter += 1
        except PermissionError:
            print(f"\n[ERROR PERMISO] No se pudo escribir en {self.csv_file}.")
            print("Cierra el archivo en Excel/LibreOffice y vuelve a presionar 'S'.\n")

def load_catalog(catalog_file='Catalogo_Instrumental.csv'):
    """Carga y valida el catálogo maestro de instrumentos."""
    catalog = {}
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cat_path = os.path.join(base_dir, catalog_file)

    if os.path.exists(cat_path):
        with open(cat_path, mode='r', encoding='utf-8-sig') as f:
            primera_linea = f.readline()
            delimitador = ';' if ';' in primera_linea else ','
            f.seek(0)
            
            reader = csv.DictReader(f, delimiter=delimitador)
            for row in reader:
                row_limpia = {k.strip(): v.strip() for k, v in row.items() if k is not None and v is not None}
                if 'instrument_id' in row_limpia and row_limpia['instrument_id']:
                    catalog[row_limpia['instrument_id']] = {
                        'nombre': row_limpia.get('nombre_instrumento', 'Desconocido'),
                        'clase': row_limpia.get('clase', 'Desconocido')
                    }
    return catalog

def main():
    print("=========================================================")
    print("      SISTEMA MULTIFASE DE ADQUISICIÓN DE DATASET       ")
    print("=========================================================")
    
    catalog = load_catalog()
    if catalog:
        print(f"[CATÁLOGO] Cargados {len(catalog)} instrumentos desde Catalogo_Instrumental.csv")
    else:
        print("[ADVERTENCIA] No se encontró Catalogo_Instrumental.csv")

    # 1. Selección de Fase
    print("\nSelecciona la Fase de Adquisición:")
    print("  1. F1_Individual (1 instrumento por toma)")
    print("  2. F2_Grupos     (Múltiples instrumentos / solapamientos)")
    print("  3. F3_Contexto   (Mano presente, bandeja, entorno real)")
    print("  4. F4_Variaciones(Cambios de luz, ángulos o distancia)")
    
    fase_opt = input("Opción (1-4) [Default 1]: ").strip()
    fases_map = {
        '1': 'F1_Individual',
        '2': 'F2_Grupos',
        '3': 'F3_Contexto',
        '4': 'F4_Variaciones'
    }
    fase_nombre = fases_map.get(fase_opt, 'F1_Individual')
    print(f"-> Fase Seleccionada: {fase_nombre}\n")

    # 2. Datos generales de la sesión
    session_id = input("ID de Sesión (ej. S01): ").strip() or "S01"
    setup_id = input("ID de Setup / Montaje (ej. ST_01): ").strip() or "ST_01"
    
    # 3. Selección de Instrumental
    instrument_ids = []
    nombres = []
    clases = []

    if fase_nombre == 'F1_Individual':
        while True:
            inst_id = input("ID del Instrumento único (ej. I01): ").strip().upper()
            if catalog and inst_id in catalog:
                instrument_ids.append(inst_id)
                nombres.append(catalog[inst_id]['nombre'])
                clases.append(catalog[inst_id]['clase'])
                print(f"   -> Encontrado: {catalog[inst_id]['nombre']} ({catalog[inst_id]['clase']})")
                break
            elif not catalog:
                instrument_ids.append(inst_id)
                nombres.append(input("   Nombre del instrumento: ").strip())
                clases.append(input("   Clase quirúrgica: ").strip())
                break
            else:
                print("   [!] ID no existe en Catalogo_Instrumental.csv. Reintenta.")
    else:
        print("Ingresa los IDs de los instrumentos en la escena separados por punto y coma (ej. I01;I02):")
        raw_ids = input("IDs: ").strip().upper().split(';')
        for inst_id in raw_ids:
            clean_id = inst_id.strip()
            if clean_id:
                instrument_ids.append(clean_id)
                if catalog and clean_id in catalog:
                    nombres.append(catalog[clean_id]['nombre'])
                    clases.append(catalog[clean_id]['clase'])
                else:
                    nombres.append("Desconocido")
                    clases.append("Desconocido")

    # 4. Parámetros de entorno y captura
    distancia = input("Distancia cámara-mesa en cm [ej. 40]: ").strip() or "40"
    iluminacion = input("ID de Iluminación [ej. L_QUIROFANO]: ").strip() or "L_QUIROFANO"
    
    mano_presente = "Sí" if fase_nombre == 'F3_Contexto' else input("¿Mano presente en la toma? (Sí/No) [No]: ").strip().capitalize() or "No"
    mano_interactua = "N/A"
    if mano_presente == "Sí":
        mano_interactua = input("¿Mano interactúa con instrumento? (Sí/No) [Sí]: ").strip().capitalize() or "Sí"

    split = input("Split (Train / Validation / Test / Pendiente) [Pendiente]: ").strip().capitalize() or "Pendiente"

    metadata = {
        'fase_nombre': fase_nombre,
        'session_id': session_id,
        'setup_id': setup_id,
        'instrument_ids': instrument_ids,
        'nombres': nombres,
        'clases': clases,
        'distancia_cm': distancia,
        'iluminacion_id': iluminacion,
        'mano_presente': mano_presente,
        'mano_interactua': mano_interactua,
        'split': split
    }

    # 5. Iniciar Capturador
    logger = SurgicalDatasetLogger(metadata, camera_index=0)
    logger.run()

if __name__ == '__main__':
    main()
