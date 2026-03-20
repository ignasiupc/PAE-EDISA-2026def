import os
import cv2
import numpy as np
from ultralytics import YOLO

# CONFIGURACIÓ
IMATGE_PROVA = "../fotos_caixa/IMG_0849.jpeg" 

model = YOLO("yolov8s-world.pt")
model.set_classes(["box"]) 

def detectar_qualsevol_caixa(ruta_imatge, mostrar_visualment=True):
    print(f"\n--- BLOC 1: YOLO-WORLD + GRABCUT ---")
    img = cv2.imread(ruta_imatge)
    if img is None:
        print("Error: No trobo la imatge.")
        return None

    img_resultat = img.copy()

    # PAS 1: DETECCIÓ AMB TEXT (Agnòstic al color)
    print("Buscant una 'box' a la imatge...")
    resultats = model.predict(img, conf=0.05, verbose=False) # Confiança baixa perquè trobi la caixa segur
    
    if resultats[0].boxes is None or len(resultats[0].boxes) == 0:
        print("YOLO-World no ha trobat cap caixa.")
        return None

    # Agafem la primera caixa que trobi
    box = resultats[0].boxes.xyxy[0].cpu().numpy()
    x1, y1, x2, y2 = map(int, box)
    
    # Afegim un petit marge a la caixa (padding) perquè GrabCut respiri millor
    marge = 10
    x1 = max(0, x1 - marge)
    y1 = max(0, y1 - marge)
    x2 = min(img.shape[1], x2 + marge)
    y2 = min(img.shape[0], y2 + marge)
    
    rect_grabcut = (x1, y1, x2 - x1, y2 - y1)
    print(f"Caixa detectada a la regió: {rect_grabcut}")
    cv2.rectangle(img_resultat, (x1, y1), (x2, y2), (255, 0, 0), 2)

    # PAS 2: GRABCUT (Separar fons i caixa sense importar el color)
    print("Aplicant GrabCut per separar la caixa del fons...")
    mascara_grabcut = np.zeros(img.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    # Executem l'algoritme (5 iteracions solen ser suficients)
    cv2.grabCut(img, mascara_grabcut, rect_grabcut, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

    # La màscara retorna valors del 0 al 3. El 1 i el 3 són l'objecte (caixa).
    mascara_final = np.where((mascara_grabcut == 2) | (mascara_grabcut == 0), 0, 255).astype('uint8')

    # PAS 3: EXTRACCIÓ DE VÈRTEXS
    contorns, _ = cv2.findContours(mascara_final, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contorns:
        print("GrabCut no ha pogut generar una silueta clara.")
        return None
        
    contorn_principal = max(contorns, key=cv2.contourArea)

    # Matemàtica per treure els punts de l'hexàgon/polígon
    perimetre = cv2.arcLength(contorn_principal, True)
    tolerancia = 0.04 * perimetre 
    vertexs = cv2.approxPolyDP(contorn_principal, tolerancia, True)

    coordenades = [(int(p[0][0]), int(p[0][1])) for p in vertexs]
    print(f"ÈXIT! S'han calculat {len(coordenades)} vèrtexs.")

    # PAS 4: PINTAR I GUARDAR EL RESULTAT
    if mostrar_visualment:
        # Dibuixem els contorns i els vèrtexs a la imatge resultat
        cv2.drawContours(img_resultat, [vertexs], -1, (0, 255, 0), 3)
        for i, (x, y) in enumerate(coordenades):
            cv2.circle(img_resultat, (x, y), 8, (0, 0, 255), -1)
            cv2.putText(img_resultat, f"P{i+1}", (x+15, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Creem la carpeta 'resultats_YOLO' si no existeix
        carpeta_sortida = "resultats_YOLO"
        os.makedirs(carpeta_sortida, exist_ok=True)

        # Extraiem el nom original de l'arxiu i el guardem
        nom_arxiu = os.path.basename(ruta_imatge)
        ruta_guardat = os.path.join(carpeta_sortida, nom_arxiu)
        cv2.imwrite(ruta_guardat, img_resultat)
        print(f"-> Imatge de debug guardada a: {ruta_guardat}")

        # Mostrem per pantalla (opcional, pots comentar aquestes línies si només vols guardar)
        cv2.namedWindow("1. Mascara GrabCut", cv2.WINDOW_NORMAL)
        cv2.namedWindow("2. Resultat Final", cv2.WINDOW_NORMAL)
        cv2.imshow("1. Mascara GrabCut", mascara_final)
        cv2.imshow("2. Resultat Final", img_resultat)
        cv2.waitKey(1) # Si posem 0: Prem una tecla a cada imatge per avançar
        cv2.destroyAllWindows()

    return coordenades

if __name__ == "__main__":
    punts = detectar_qualsevol_caixa(IMATGE_PROVA)