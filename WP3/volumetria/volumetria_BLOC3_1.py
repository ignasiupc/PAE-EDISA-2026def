import os
import cv2
import statistics

# ==========================================
# CONFIGURACIÓ DE L'ENTORN
# ==========================================
DISTANCIA_LIDAR_CM = 60.0  
DISTANCIA_FOCAL_PX = 2976.74 
# ==========================================

def calcular_volumetria(ruta_carpeta, diccionari_punts):
    print("\n--- MOTOR PARAL·LAXI (DRON PARAL·LEL) ACTIVAT (AUTOMÀTIC) ---")
    
    if not diccionari_punts:
        print("Error: No s'han rebut dades del BLOC 1.")
        return

    resultats_amplada = []
    resultats_profunditat = []
    resultats_alcada = []
    
    for nom_imatge, punts in diccionari_punts.items():
        # FILTRE PREVI: Una caixa en perspectiva necessita almenys 5 o 6 punts per definir 2 cares.
        # Si té 4 punts, és una cara plana o un error de la IA (ex: la motxilla)
        if len(punts) < 5:
            print(f"[{nom_imatge}] DESCARTADA: Objecte pla detectat ({len(punts)} vèrtexs). La IA ha fallat.")
            continue

        ruta_completa = os.path.join(ruta_carpeta, nom_imatge)
        img = cv2.imread(ruta_completa)
        
        if img is None:
            continue
            
        ample = img.shape[1]
        cx = ample / 2.0  

        # ------------------------------------------------------------------
        # TRADUCCIÓ DIRECTA ALS TEUS CLICS MANUALS
        # ------------------------------------------------------------------
        x_coords = [p[0] for p in punts]
        y_coords = [p[1] for p in punts]

        x_esq = min(x_coords)  
        x_dre = max(x_coords)  
        y_dalt = min(y_coords) 
        y_baix = max(y_coords) 
        
        # L'aresta central sol coincidir amb el vèrtex més baix de la imatge
        p_bottom = punts[y_coords.index(y_baix)]
        x_cen = float(p_bottom[0])

        w_cara_1_px = abs(x_cen - x_esq)
        w_cara_2_px = abs(x_dre - x_cen)
        h_caixa_px = abs(y_baix - y_dalt)
        # ------------------------------------------------------------------

        if w_cara_1_px < w_cara_2_px:
            amplada_px = w_cara_2_px
            u_front = abs(x_cen - cx)
            u_back = abs(x_esq - cx)
        else:
            amplada_px = w_cara_1_px
            u_front = abs(x_cen - cx)
            u_back = abs(x_dre - cx)
            
        # LA TEVA LÒGICA INTACTA (Sense intercanvis tramposos)
        if u_back >= u_front:
            print(f"[{nom_imatge}] DESCARTADA: Càmera rotada o asimetria en la segmentació de la IA.")
            continue
            
        if u_back < 1: 
            u_back = 1 
        
        # Càlculs físics (la teva fórmula exacta)
        profunditat_cm = DISTANCIA_LIDAR_CM * ((u_front / u_back) - 1.0)
        amplada_cm = (amplada_px * DISTANCIA_LIDAR_CM) / DISTANCIA_FOCAL_PX
        alcada_cm = (h_caixa_px * DISTANCIA_LIDAR_CM) / DISTANCIA_FOCAL_PX
        
        resultats_amplada.append(amplada_cm)
        resultats_profunditat.append(profunditat_cm)
        resultats_alcada.append(alcada_cm)
        
        print(f"[{nom_imatge}] OK -> Profunditat estirada a: {profunditat_cm:.1f} cm (Ample: {amplada_cm:.1f} cm, Alt: {alcada_cm:.1f} cm)")
        
    # ==========================================
    # RESULTATS FINALS
    # ==========================================
    if not resultats_profunditat:
        print("\nError: Cap de les fotos ha generat una geometria vàlida per al paral·laxi.")
        return
        
    amp_final = statistics.median(resultats_amplada)
    prof_final = statistics.median(resultats_profunditat)
    alc_final = statistics.median(resultats_alcada)
    volum_final = amp_final * prof_final * alc_final
    
    print("\n==========================================")
    print(f" RESULTATS FINALS DRON ({len(resultats_profunditat)} FOTOS VÀLIDES)")
    print("==========================================")
    print(f"Amplada (Frontal):    {amp_final:.1f} cm")
    print(f"Profunditat (Lateral):{prof_final:.1f} cm")
    print(f"Alçada estimada:      {alc_final:.1f} cm")
    print("------------------------------------------")
    print(f"VOLUM TOTAL:          {volum_final:.2f} cm³")
    print("==========================================")