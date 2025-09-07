import os
import numpy as np

HEATMAP_DIR = "./heatmaps"
os.makedirs(HEATMAP_DIR, exist_ok=True)

def cargar_heatmap(nombre):
    """
    Carga un heatmap precomputado de {HEATMAP_DIR}/{nombre}.npy
    """
    path = os.path.join(HEATMAP_DIR, f"{nombre}.npy")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No existe el heatmap precomputado: {path}")
    return np.load(path)
