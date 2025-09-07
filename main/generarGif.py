import os
import imageio.v2 as imageio

def generar_gif(num_generaciones, carpeta_imgs, nombre_salida, duracion=500):
    """
    Genera un GIF a partir de imágenes numeradas secuencialmente.

    - num_generaciones: cantidad de frames a incluir
    - carpeta_imgs: carpeta donde están las imágenes
    - nombre_salida: nombre del archivo GIF resultante (con .gif)
    - duracion: segundos por frame (float)
    """
    # Lista de archivos en orden
    imagenes = [os.path.join(carpeta_imgs, f"gif/generacion_{i}.png") for i in range(num_generaciones)]

    # Filtrar solo las que existen (por si falta alguna)
    imagenes = [img for img in imagenes if os.path.exists(img)]

    # Leer imágenes
    frames = [imageio.imread(img) for img in imagenes]

    # Guardar GIF
    imageio.mimsave(nombre_salida, frames, duration=duracion)
    print(f"GIF generado: {nombre_salida} ({len(frames)} frames, {duracion}s/frame)")
