import os
import math
import numpy as np
import matplotlib.pyplot as plt

try:
    from noise import pnoise2  # Para Perlin Noise
except ImportError:
    pnoise2 = None

# =========================
# Directorio de caché
# =========================
HEATMAP_DIR = "./heatmaps"
os.makedirs(HEATMAP_DIR, exist_ok=True)

# =========================
# Generación de un heatmap
# =========================
def generar_heatmap(size, tipo="distancia", **kwargs):
    heatmap = np.zeros((size, size))
    centro = kwargs.get("centro", (size // 2, size // 2))

    if tipo == "distancia":
        X, Y = np.meshgrid(np.arange(size), np.arange(size), indexing="ij")
        dist = np.hypot(X - centro[0], Y - centro[1])
        heatmap = 1 / (1 + dist)

    elif tipo == "distancia_suave":
        # Gradiente gaussiano centrado
        sigma = kwargs.get("sigma", size / 3)  
        X, Y = np.meshgrid(np.arange(size), np.arange(size), indexing="ij")
        dist = np.hypot(X - centro[0], Y - centro[1])
        heatmap = np.exp(-(dist**2) / (2 * sigma**2))
        # Normalizar a [0,1]
        heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min())

    elif tipo == "random":
        heatmap = np.random.rand(size, size)

    elif tipo == "perlin":
        if pnoise2 is None:
            raise ImportError("Instala la librería 'noise' para usar Perlin Noise")
        escala = kwargs.get("escala", 50.0)
        octavas = kwargs.get("octavas", 4)
        for x in range(size):
            for y in range(size):
                heatmap[x, y] = pnoise2(x / escala, y / escala, octaves=octavas)
        heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min())

    elif tipo == "gradiente":
        x = np.linspace(0, 1, size)
        heatmap = np.tile(x, (size, 1))

    elif tipo == "blobs":
        num_blobs = kwargs.get("num_blobs", 5)
        radio_min = kwargs.get("radio_min", 10)
        radio_max = kwargs.get("radio_max", 40)
        X, Y = np.meshgrid(np.arange(size), np.arange(size), indexing="ij")
        for _ in range(num_blobs):
            cx, cy = np.random.randint(0, size, 2)
            intensidad = np.random.uniform(0.5, 1.0)
            radio = np.random.randint(radio_min, radio_max)
            dist = np.hypot(X - cx, Y - cy)
            heatmap += intensidad * np.exp(-(dist**2) / (2 * radio**2))
        heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min())

    else:
        raise ValueError(f"Tipo de heatmap '{tipo}' no reconocido")

    return heatmap


# =========================
# Caché y recarga automática
# =========================
def cargar_heatmap(nombre, size, tipo="distancia", **params):
    """
    Carga de ./heatmaps/{nombre}_{tipo}.npy o genera+guarda si no existe.
    """
    fname = f"{nombre}_{tipo}.npy"
    path = os.path.join(HEATMAP_DIR, fname)
    if os.path.exists(path):
        return np.load(path)

    heatmap = generar_heatmap(size, tipo=tipo, **params)
    np.save(path, heatmap)
    return heatmap

# =========================
# Mostrar múltiples heatmaps
# =========================
def mostrar_varios_heatmaps(configs, size, cols=3, cmap="viridis"):
    """
    configs: lista de dicts con keys: 'nombre', 'tipo', y params opcionales
    size: dimensión de cada heatmap
    cols: número de columnas en la cuadrícula de visualización
    """
    n = len(configs)
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(4*cols, 4*rows))

    for ax, cfg in zip(axes.flat, configs):
        hm = cargar_heatmap(
            nombre=cfg["nombre"],
            size=size,
            tipo=cfg["tipo"],
            **{k:v for k,v in cfg.items() if k not in ("nombre","tipo")}
        )
        ax.imshow(hm, origin="lower", cmap=cmap)
        ax.set_title(f"{cfg['nombre']} ({cfg['tipo']})")
        ax.axis("off")

    # apaga ejes sobrantes
    for ax in axes.flat[n:]:
        ax.axis("off")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # =========================
    # Define aquí tu diversidad de mapas
    # =========================
    heatmap_configs = [
        {"nombre": "distancia_centro", "tipo": "distancia_suave"},
        {"nombre": "aleatorio",      "tipo": "random"},
        {"nombre": "perlin_fina",    "tipo": "perlin",  "escala": 100.0, "octavas": 3},
        {"nombre": "perlin_gruesa",  "tipo": "perlin",  "escala": 800.0, "octavas": 5},
        {"nombre": "grad_horizontal","tipo": "gradiente"},
        {"nombre": "manchas_peq",    "tipo": "blobs",    "num_blobs": 20, "radio_min": 5,  "radio_max": 20},
        {"nombre": "manchas_med",  "tipo": "blobs",    "num_blobs": 14,  "radio_min": 30, "radio_max": 120},
        {"nombre": "manchas_grand",  "tipo": "blobs",    "num_blobs": 5,  "radio_min": 70, "radio_max": 180},
    ]

    # =========================
    # Generar y visualizar
    # =========================
    mostrar_varios_heatmaps(heatmap_configs, size=1000, cols=3)
