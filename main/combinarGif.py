import os
import math
import numpy as np
import imageio

def combinar_gifs_en_grilla(gif_paths, output_path, cols=None, duration=0.1, gap=5):
    """
    Combina varios GIFs en una grilla de hasta 4 columnas por fila,
    creando más filas si hay más de 4 GIFs.

    gif_paths:   lista de rutas a archivos .gif
    output_path: ruta al GIF resultante
    cols:        número de columnas (por defecto 4 si cols es None)
    duration:    segundos por frame
    gap:         separación (px) entre celdas
    """
    # Lectores de cada GIF y conteo de frames mínimos
    readers = [imageio.get_reader(p) for p in gif_paths]
    n_frames = min(r.get_length() for r in readers)
    n_gifs    = len(gif_paths)

    # Fijar 4 columnas si no se pasa otro valor
    if cols is None:
        cols = 4
    rows = math.ceil(n_gifs / cols)

    # Dimensiones de muestra
    sample = readers[0].get_data(0)
    h, w   = sample.shape[:2]
    pad_w  = np.zeros((h, gap, 3), dtype=np.uint8)

    final_frames = []
    for i in range(n_frames):
        # Leer cada frame (o negro si no existe)
        frames = []
        for r in readers:
            try:
                frame = r.get_data(i)
            except IndexError:
                frame = np.zeros((h, w, 3), dtype=np.uint8)
            if frame.ndim == 2:
                frame = np.stack([frame]*3, axis=2)
            elif frame.shape[2] == 4:
                frame = frame[..., :3]
            frames.append(frame)

        # Construir filas de hasta 'cols' imágenes
        grid_rows = []
        for ry in range(rows):
            row_imgs = []
            for cx in range(cols):
                idx = ry * cols + cx
                img = frames[idx] if idx < len(frames) else np.zeros((h, w, 3), dtype=np.uint8)
                if cx > 0:
                    row_imgs.append(pad_w)
                row_imgs.append(img)
            grid_rows.append(np.hstack(row_imgs))

        # Normalizar anchos de fila
        max_w = max(r.shape[1] for r in grid_rows)
        norm_rows = []
        for row in grid_rows:
            if row.shape[1] < max_w:
                extra = max_w - row.shape[1]
                pad   = np.zeros((h, extra, 3), dtype=np.uint8)
                row   = np.hstack([row, pad])
            norm_rows.append(row)

        # Apilar filas con separación horizontal
        grid_with_gap = []
        for ry, row in enumerate(norm_rows):
            if ry > 0:
                pad_h = np.zeros((gap, max_w, 3), dtype=np.uint8)
                grid_with_gap.append(pad_h)
            grid_with_gap.append(row)

        final_frames.append(np.vstack(grid_with_gap))

    # Escribir GIF final
    with imageio.get_writer(output_path, mode='I', duration=duration) as writer:
        for frame in final_frames:
            writer.append_data(frame)

    for r in readers:
        r.close()


if __name__ == "__main__":
    base_dir = "./gif"
    for carpeta in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, carpeta)
        if not os.path.isdir(folder_path):
            continue

        gif_paths = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(".gif")
        ]
        if not gif_paths:
            print(f"[SKIP] No hay GIFs en {folder_path}")
            continue

        output_path = os.path.join(base_dir, f"{carpeta}.gif")
        print(f"[COMBINING] {len(gif_paths)} GIFs en '{carpeta}' → {output_path}")

        combinar_gifs_en_grilla(
            gif_paths=gif_paths,
            output_path=output_path,
            cols=None,      # None → se fija a 4 columnas por fila
            duration=0.12,
            gap=5
        )

    print("¡Todos los GIFs combinados han sido generados!")
