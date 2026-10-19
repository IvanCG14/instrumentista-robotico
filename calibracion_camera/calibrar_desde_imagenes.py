import cv2
import numpy as np
import os
import glob
import yaml
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DEL PATRÓN Y DIRECTORIOS
# ==========================================
CORNERS_X = 9
CORNERS_Y = 6
CHESSBOARD_SIZE = (CORNERS_X, CORNERS_Y)
SQUARE_SIZE_MM = 15.0

IMG_DIR = "imagenes_calibracion"
RES_DIR = "resultados_calibracion"
os.makedirs(RES_DIR, exist_ok=True)

CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Puntos 3D reales del tablero (Z=0)
objp = np.zeros((CORNERS_X * CORNERS_Y, 3), np.float32)
objp[:, :2] = np.mgrid[0:CORNERS_X, 0:CORNERS_Y].T.reshape(-1, 2) * SQUARE_SIZE_MM

def cargar_y_procesar_imagenes():
    # Buscar todas las imágenes .jpg y .png en la carpeta
    rutas = sorted(glob.glob(os.path.join(IMG_DIR, "*.jpg"))) + sorted(glob.glob(os.path.join(IMG_DIR, "*.png")))
    
    if not rutas:
        print(f"Error: No se encontraron imágenes en '{IMG_DIR}'.")
        return None, None, None

    print(f"Se encontraron {len(rutas)} imágenes en '{IMG_DIR}'. Buscando esquinas...\n")

    objpoints = []
    imgpoints = []
    image_size = None
    imagenes_validas = 0

    for fname in rutas:
        img = cv2.imread(fname)
        if img is None:
            continue
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if image_size is None:
            image_size = (gray.shape[1], gray.shape[0])

        ret, corners = cv2.findChessboardCorners(gray, CHESSBOARD_SIZE, None)

        if ret:
            corners_refined = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), CRITERIA)
            objpoints.append(objp)
            imgpoints.append(corners_refined)
            imagenes_validas += 1
            print(f"[OK] Patrón detectado en: {os.path.basename(fname)}")
        else:
            print(f"[OMITIDA] No se detectó el patrón completo en: {os.path.basename(fname)}")

    print(f"\nResumen: {imagenes_validas} de {len(rutas)} imágenes fueron válidas para la calibración.")
    return objpoints, imgpoints, image_size

def calcular_error_reproyeccion(objpoints, imgpoints, rvecs, tvecs, mtx, dist):
    total_error = 0
    total_points = 0
    errores_por_imagen = []
    
    for i in range(len(objpoints)):
        imgpoints_proyectados, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        
        p_real = imgpoints[i].reshape(-1, 2).astype(np.float32)
        p_proy = imgpoints_proyectados.reshape(-1, 2).astype(np.float32)
        
        error = cv2.norm(p_real, p_proy, cv2.NORM_L2) / len(p_proy)
        errores_por_imagen.append(error)
        total_error += error
        total_points += 1
        
    error_medio = total_error / total_points
    return error_medio, errores_por_imagen

def calibrar_desde_disco():
    objpoints, imgpoints, image_size = cargar_y_procesar_imagenes()

    if not objpoints or len(objpoints) < 5:
        print("\nNo hay suficientes imágenes válidas para calibrar (se recomiendan al menos 10).")
        return

    print("\nIniciando cálculo de parámetros intrínsecos...")
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, image_size, None, None)

    error_medio, errores_por_img = calcular_error_reproyeccion(objpoints, imgpoints, rvecs, tvecs, mtx, dist)

    print("\n================ RESULTADOS ================")
    print(f"Error RMS de reproyección: {ret:.4f} píxeles")
    print(f"Error Medio cálculo manual: {error_medio:.4f} píxeles")
    print(f"Matriz de la cámara (K):\n{mtx}")
    print(f"Coeficientes de distorsión:\n{dist.ravel()}")
    print("============================================")

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

if __name__ == "__main__":
    calibrar_desde_disco()
