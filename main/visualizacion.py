import matplotlib.pyplot as plt
import numpy as np

def mostrar_varios_conjuntos(
    lista_coords,
    size,
    etiquetas=None,
    colores=None,
    titulo="Múltiples conjuntos de coordenadas",
    heatmap=None,
    guardar_como=None,   # Nuevo parámetro opcional
    dpi=300              # Resolución de guardado
):
    plt.figure(figsize=(6, 6))

    # Si hay mapa de calor, dibujarlo primero
    if heatmap is not None:
        heatmap = np.array(heatmap)
        plt.imshow(
            heatmap,
            cmap='RdYlGn_r',      # Verde → Amarillo → Rojo
            origin='upper',       # Para que coincida con la inversión de ejes
            extent=(-0.5, size - 0.5, size - 0.5, -0.5)
        )

    plt.xlim(-0.5, size - 0.5)
    plt.ylim(-0.5, size - 0.5)
    plt.gca().invert_yaxis()

    if etiquetas is None:
        etiquetas = [f"Conjunto {i+1}" for i in range(len(lista_coords))]
    if colores is None:
        cmap = plt.cm.get_cmap('tab10', len(lista_coords))
        colores = [cmap(i) for i in range(len(lista_coords))]

    for coords, etiqueta, color in zip(lista_coords, etiquetas, colores):
        if coords:
            # Extraer solo las coordenadas (x, y)
            puntos = [p[0] if isinstance(p[0], tuple) else p for p in coords]
            xs, ys = zip(*puntos)
            cantidad = len(puntos)
            plt.scatter(ys, xs, c=[color], edgecolors='black', s=80,
                        label=f"{etiqueta} ({cantidad})")

    plt.title(titulo)
    plt.legend()

    # Guardar imagen si se especifica
    if guardar_como:
        plt.savefig(guardar_como, dpi=dpi, bbox_inches='tight')
        print(f"Imagen guardada en: {guardar_como}")

    plt.show()
