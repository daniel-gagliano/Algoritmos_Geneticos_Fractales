import os
import numpy as np
import imageio.v2 as imageio

def generar_gif(num_generaciones, carpeta_imgs, nombre_salida, duracion=0.5):
    """
    Genera un GIF a partir de imágenes PNG numeradas secuencialmente.

    - num_generaciones: número máximo de imágenes (0 … num_generaciones-1)
    - carpeta_imgs:     carpeta donde están las PNG (p. ej. "./gif")
    - nombre_salida:    ruta/nombre del GIF resultante (debe terminar en .gif)
    - duracion:         segundos por frame (float; p. ej. 0.5)
    """
    # Construir rutas esperadas y filtrar las que existen
    rutas = [
        os.path.join(carpeta_imgs, f"generacion_{i}.png")
        for i in range(num_generaciones)
    ]
    rutas_existentes = []
    for ruta in rutas:
        if os.path.isfile(ruta):
            rutas_existentes.append(ruta)
        else:
            print(f"Aviso: no se encontró {ruta}, se omitirá")

    if not rutas_existentes:
        print("Error: no hay imágenes válidas para generar el GIF.")
        return

    # Leer y normalizar canales (RGB)
    frames = []
    for ruta in rutas_existentes:
        img = imageio.imread(ruta)
        # Escala de grises -> RGB
        if img.ndim == 2:
            img = np.stack([img] * 3, axis=-1)
        # RGBA -> RGB (descarta canal alpha)
        elif img.ndim == 3 and img.shape[2] == 4:
            img = img[..., :3]
        frames.append(img)

    # Escribir el GIF
    with imageio.get_writer(nombre_salida, mode='I', duration=duracion) as writer:
        for frame in frames:
            writer.append_data(frame)

    print(f"GIF generado: {nombre_salida} — {len(frames)} frames, {duracion}s/frame")


if __name__ == "__main__":
    # Ejemplo de uso
    num_generaciones = 50
    carpeta_imgs     = "./gif"
    nombre_salida    = "evolucion.gif"
    duracion         = 0.12  # 120 ms por frame

    generar_gif(num_generaciones, carpeta_imgs, nombre_salida, duracion)
