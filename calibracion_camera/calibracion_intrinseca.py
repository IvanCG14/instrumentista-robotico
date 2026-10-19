import cv2
import numpy as np
import os
import glob
import yaml
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DEL PATRÓN Y DIRECTORIOS
# ==========================================
# 7x10 cuadros = 6x9 esquinas interiores. OpenCV usa (columnas, filas)
CORNERS_X = 9
CORNERS_Y = 6
CHESSBOARD_SIZE = (CORNERS_X, CORNERS_Y)

# Tamaño real del cuadro impreso (en milímetros)
SQUARE_SIZE_MM = 15.0

# Directorios de trabajo
IMG_DIR = "imagenes_calibracion"
RES_DIR = "resultados_calibracion"
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)

# Criterios de parada para el refinamiento subpíxel
# (Tipo de criterio, número máximo de iteraciones, precisión deseada)
CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Puntos 3D reales del tablero (Z=0). Estructura: (0,0,0), (15,0,0), (30,0,0)...
objp = np.zeros((CORNERS_X * CORNERS_Y, 3), np.float32)
objp[:, :2] = np.mgrid[0:CORNERS_X, 0:CORNERS_Y].T.reshape(-1, 2) * SQUARE_SIZE_MM

def capturar_y_revisar_imagenes(camera_index=0, width=1920, height=1080):
    """
    Inicia la cámara, permite capturar imágenes, detecta esquinas y pide validación al usuario.
    """
    cap = cv2.VideoCapture(camera_index)
    
    # Intentar forzar la resolución (ej. 4K o 1080p)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    # Comprobar la resolución real obtenida
    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Resolución de captura configurada: {actual_w}x{actual_h}")

    objpoints = [] # Puntos 3D en el espacio real
    imgpoints = [] # Puntos 2D en el plano de la imagen
    valid_images_count = 0

    print("\n--- CONTROLES DE CAPTURA ---")
    print("[C] - Capturar frame y buscar patrón")
    print("[Q] - Terminar captura y proceder a calibrar")

    # --- AGREGA ESTAS DOS LÍNEAS ---
    cv2.namedWindow('Live - Logitech MX Brio', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Live - Logitech MX Brio', 960, 540)
    # -------------------------------

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al acceder a la cámara.")
            break

        # Mostrar HUD
        display_frame = frame.copy()
        cv2.putText(display_frame, f"Capturas validas: {valid_images_count} | [C] Capturar | [Q] Salir", 
                    (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow('Live - Logitech MX Brio', display_frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('c'):
            print("\nBuscando esquinas... (Puede tardar unos segundos en altas resoluciones)")
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Buscar esquinas
            ret_corners, corners = cv2.findChessboardCorners(gray, CHESSBOARD_SIZE, None)

            if ret_corners:
                # Refinamiento subpíxel
                corners_refined = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), CRITERIA)
                
                # Dibujar para validación
                preview = frame.copy()
                cv2.drawChessboardCorners(preview, CHESSBOARD_SIZE, corners_refined, ret_corners)
                
                # Redimensionar la vista previa si es muy grande (ej. 4K) para que quepa en pantalla
                h, w = preview.shape[:2]
                if w > 1280:
                    preview = cv2.resize(preview, (1280, int(h * 1280 / w)))

                cv2.imshow('Validacion - ¿Mantener?', preview)
                print("Esquinas detectadas. Presiona [K] para Mantener (Keep) o [D] para Descartar (Discard).")
                
                while True:
                    val_key = cv2.waitKey(0) & 0xFF
                    if val_key == ord('k'):
                        objpoints.append(objp)
                        imgpoints.append(corners_refined)
                        img_name = os.path.join(IMG_DIR, f"calib_{valid_images_count:03d}.jpg")
                        cv2.imwrite(img_name, frame)
                        valid_images_count += 1
                        print(f"Imagen guardada: {img_name}")
                        break
                    elif val_key == ord('d'):
                        print("Imagen descartada.")
                        break
                cv2.destroyWindow('Validacion - ¿Mantener?')
            else:
                print("No se encontró el patrón de forma completa. Intenta otro ángulo/iluminación.")

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return objpoints, imgpoints, (actual_w, actual_h)

def calcular_error_reproyeccion(objpoints, imgpoints, rvecs, tvecs, mtx, dist):
    """Calcula el error de reproyección global y por imagen."""
    total_error = 0
    total_points = 0
    errores_por_imagen = []
    
    for i in range(len(objpoints)):
        imgpoints_proyectados, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        
        # Formatear ambas matrices con la misma estructura (N, 2) y tipo de dato
        p_real = imgpoints[i].reshape(-1, 2).astype(np.float32)
        p_proy = imgpoints_proyectados.reshape(-1, 2).astype(np.float32)
        
        error = cv2.norm(p_real, p_proy, cv2.NORM_L2) / len(p_proy)
        errores_por_imagen.append(error)
        total_error += error
        total_points += 1
        
    error_medio = total_error / total_points
    return error_medio, errores_por_imagen

def calibrar_camara():
    # 1. Fase de captura
    objpoints, imgpoints, image_size = capturar_y_revisar_imagenes(camera_index=2, width=1920, height=1080)
    
    if len(objpoints) < 10:
        print(f"\n¡CUIDADO! Tienes {len(objpoints)} imágenes. Se recomiendan al menos 20 para una buena calibración.")
        confirm = input("¿Deseas continuar de todos modos? (s/n): ")
        if confirm.lower() != 's':
            return

    print("\nIniciando cálculo de parámetros intrínsecos...")
    # 2. Calibración principal
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, image_size, None, None)

    # 3. Cálculo de errores
    error_medio, errores_por_img = calcular_error_reproyeccion(objpoints, imgpoints, rvecs, tvecs, mtx, dist)

    # 4. Mostrar y guardar resultados
    print("\n================ RESULTADOS ================")
    print(f"Error RMS de reproyección: {ret:.4f} píxeles")
    print(f"Error Medio calculo manual: {error_medio:.4f} píxeles")
    print(f"Matriz de la cámara (K):\n{mtx}")
    print(f"Coeficientes de distorsión:\n{dist.ravel()}")
    print("============================================")

    # Guardar en YAML
    datos_calibracion = {
        'fecha_calibracion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'resolucion': list(image_size),
        'tamaño_cuadro_mm': SQUARE_SIZE_MM,
        'dimensiones_patron': list(CHESSBOARD_SIZE),
        'num_imagenes_validas': len(objpoints),
        'error_rms': float(ret),
        'matriz_camara': mtx.tolist(),
        'coeficientes_distorsion': dist.tolist()
    }

    yaml_path = os.path.join(RES_DIR, 'parametros_intrinsecos.yaml')
    with open(yaml_path, 'w') as f:
        yaml.dump(datos_calibracion, f, default_flow_style=False)
    print(f"\nParámetros guardados exitosamente en: {yaml_path}")

    # 5. Rectificación de prueba (Visualización)
    if len(objpoints) > 0:
        print("\nRectificando la última imagen capturada como prueba...")
        img_prueba = cv2.imread(os.path.join(IMG_DIR, f"calib_{len(objpoints)-1:03d}.jpg"))
        h, w = img_prueba.shape[:2]
        
        # Obtener nueva matriz óptima (para evitar recorte de bordes)
        new_mtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
        
        # Undistort
        dst = cv2.undistort(img_prueba, mtx, dist, None, new_mtx)
        
        # Recortar imagen si es necesario basado en ROI
        x, y, w_roi, h_roi = roi
        dst_recortada = dst[y:y+h_roi, x:x+w_roi]

        # Mostrar lado a lado (redimensionando por pantalla)
        combinada = np.hstack((cv2.resize(img_prueba, (640, 360)), cv2.resize(dst, (640, 360))))
        cv2.imshow("IZQ: Original | DER: Rectificada", combinada)
        print("Presiona cualquier tecla en la ventana de imagen para salir.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    calibrar_camara()
