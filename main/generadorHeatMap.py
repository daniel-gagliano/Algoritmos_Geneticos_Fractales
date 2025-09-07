import numpy as np
import math
try:
    from noise import pnoise2  # Para Perlin Noise
except ImportError:
    pnoise2 = None

def generar_heatmap(size, tipo="distancia", **kwargs):
    """
    Genera un mapa de calor de tamaño size x size según el tipo especificado.
    Tipos soportados:
      - "distancia": inverso de la distancia a un punto centro
      - "random": ruido aleatorio uniforme
      - "perlin": ruido Perlin 2D (requiere librería noise)
      - "gradiente": gradiente horizontal
      - "blobs": manchas gaussianas aleatorias
    """
    heatmap = np.zeros((size, size))
    centro = kwargs.get("centro", (size // 2, size // 2))

    if tipo == "distancia":
        for x in range(size):
            for y in range(size):
                dist = math.hypot(x - centro[0], y - centro[1])
                heatmap[x, y] = 1 / (1 + dist)

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
        # Normalizar entre 0 y 1
        heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min())

    elif tipo == "gradiente":
        x = np.linspace(0, 1, size)
        heatmap = np.tile(x, (size, 1))

    elif tipo == "blobs":
        num_blobs = kwargs.get("num_blobs", 5)
        for _ in range(num_blobs):
            cx, cy = np.random.randint(0, size, 2)
            intensidad = np.random.uniform(0.5, 1.0)
            radio = np.random.randint(10, 40)
            for x in range(size):
                for y in range(size):
                    dist = np.hypot(x - cx, y - cy)
                    heatmap[x, y] += intensidad * np.exp(-(dist**2) / (2 * radio**2))
        # Normalizar
        heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min())

    else:
        raise ValueError(f"Tipo de heatmap '{tipo}' no reconocido")

    return heatmap
