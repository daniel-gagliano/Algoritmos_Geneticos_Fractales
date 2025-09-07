import matplotlib.pyplot as plt
import numpy as np

def mostrar_varios_conjuntos(
    lista_coords,
    size,
    etiquetas=None,
    colores=None,
    titulo="Múltiples conjuntos de coordenadas",  # se sigue recibiendo
    heatmap=None,
    guardar_como=None,
    dpi=100
):
    """
    Dibuja los puntos (y opcionalmente un heatmap) sin título, sin ejes,
    sin leyenda y sin márgenes blancos. El parámetro 'titulo' queda
    disponible para nombrar el archivo, pero no se dibuja.
    """
    # Crear figura y eje
    fig, ax = plt.subplots(figsize=(6, 6))

    # Mostrar heatmap de fondo si existe
    if heatmap is not None:
        ax.imshow(
            np.array(heatmap),
            cmap='RdYlGn_r',
            origin='upper',
            extent=(-0.5, size - 0.5, size - 0.5, -0.5)
        )

    # Preparar colores por defecto
    n = len(lista_coords)
    if colores is None:
        cmap   = plt.cm.get_cmap('tab10', n)
        colores = [cmap(i) for i in range(n)]

    # Pintar los conjuntos de puntos
    for coords, color in zip(lista_coords, colores):
        if not coords:
            continue
        puntos = [p[0] if isinstance(p[0], tuple) else p for p in coords]
        xs, ys = zip(*puntos)
        ax.scatter(
            ys, xs,
            c=[color],
            edgecolors='black',
            s=80
        )

    # Ajustar límites / orientar
    ax.set_xlim(-0.5, size - 0.5)
    ax.set_ylim(size - 0.5, -0.5)
    ax.invert_yaxis()

    # Quitar ejes y ticks
    ax.axis('off')

    # Eliminar márgenes blancos
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    fig.patch.set_alpha(0)  # fondo transparente (opcional)

    # Guardar la imagen
    if guardar_como:
        fig.savefig(
            guardar_como,
            dpi=dpi,
            bbox_inches='tight',
            pad_inches=0
        )

    plt.close(fig)
