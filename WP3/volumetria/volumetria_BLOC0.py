import os
import cv2

# Importem els nostres mòduls (Assegura't que els arxius es diguin així)
from volumetria_BLOC1 import detectar_qualsevol_caixa
from volumetria_BLOC3_1 import calcular_volumetria

# ==========================================
# CONFIGURACIÓ GENERAL
# ==========================================
CARPETA_FOTOS = "../fotos_caixa"
# ==========================================

def executar_pipeline_complet():
    print(f"=== INICIANT SISTEMA DE VOLUMETRIA ===")
    print(f"Buscant imatges a la carpeta: {CARPETA_FOTOS}...\n")

    # Comprovem si la carpeta existeix
    if not os.path.exists(CARPETA_FOTOS):
        print(f"Error: La carpeta {CARPETA_FOTOS} no existeix.")
        return

    # Llista de tots els arxius que siguin imatges
    arxius = [f for f in os.listdir(CARPETA_FOTOS) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not arxius:
        print("No s'han trobat imatges a la carpeta.")
        return

    print(f"S'han trobat {len(arxius)} imatges. Processant...\n")

    # Aquest diccionari guardarà: {"nom_foto.jpg": [(x,y), (x,y), ...]}
    base_de_dades_vertexs = {}

    # BUCLE PRINCIPAL: Executar BLOC 1 per cada foto
    for nom_arxiu in arxius:
        ruta_completa = os.path.join(CARPETA_FOTOS, nom_arxiu)
        
        # Cridem el BLOC 1 (amb mostrar_visualment=False perquè no s'aturi)
        punts = detectar_qualsevol_caixa(ruta_completa, mostrar_visualment=True)
        
        if punts is not None and len(punts) > 0:
            base_de_dades_vertexs[nom_arxiu] = punts
            print(f"[OK] {nom_arxiu} -> {len(punts)} vèrtexs extrets.")
        else:
            print(f"[FAIL] {nom_arxiu} -> No s'ha pogut processar la caixa.")

    print("\n=== RESUM DE L'EXTRACCIÓ ===")
    print(f"Caixes processades amb èxit: {len(base_de_dades_vertexs)}/{len(arxius)}\n")

    # ========================================================
    # CONNEXIÓ AMB EL BLOC 3.1 (Matemàtiques i Volum)
    # ========================================================
    if len(base_de_dades_vertexs) > 0:

        calcular_volumetria(CARPETA_FOTOS, base_de_dades_vertexs)
        print(f"Dades enviades: {base_de_dades_vertexs}")
    else:
        print("El sistema s'ha aturat perquè no hi ha dades per al BLOC 3.")

if __name__ == "__main__":
    executar_pipeline_complet()