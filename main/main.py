import os
import math
import random
import json
import argparse

from algoritmo import (
    generar_pozos_aleatorios,
    generar_pozos_equidistantes,
    cruce_interno_centro,
    seleccionar_poblacion
)
from visualizacion import mostrar_varios_conjuntos
from cargarHeatMap import cargar_heatmap
from generarGif import generar_gif

def fitness_con_penalizacion(p, heatmap, poblacion, dist_min, penal_max):
    base = heatmap[p[0], p[1]]
    penal = 0
    for q in poblacion:
        q_pt = q[0] if isinstance(q[0], tuple) else q
        d = math.hypot(p[0] - q_pt[0], p[1] - q_pt[1])
        if d < dist_min:
            penal += penal_max * (1 - d / dist_min)
    return base - penal

def main(config_path):
    # Leer escenarios del JSON
    with open(config_path, 'r', encoding='utf-8') as f:
        escenarios = json.load(f)

    base = os.path.splitext(os.path.basename(config_path))[0]

    # Directorios raíz únicos
    img_root = "./img"
    gif_root = "./gif"
    os.makedirs(img_root, exist_ok=True)
    os.makedirs(gif_root, exist_ok=True)

    for cfg in escenarios:
        nombre = cfg["nombre"]

        # Carpeta para las imágenes de este escenario
        carpeta_imgs = os.path.join(img_root, base, nombre)
        os.makedirs(carpeta_imgs, exist_ok=True)

        heatmap = cargar_heatmap(nombre)
        size    = heatmap.shape[0]

        puntos       = cfg["puntos"]
        generaciones = cfg["generaciones"]
        jitter       = cfg["jitter"]
        porc_sel     = cfg["porcentaje_seleccion"]
        num_sel      = cfg["num_seleccionados"]
        dist_min     = cfg["distancia_min"]
        penal_max    = cfg["penalizacion_max"]

        # Población inicial según modo
        if cfg["modo"] == "equidistantes":
            pozos, poblacion = generar_pozos_equidistantes(
                num_pozos     = puntos,
                grid_size     = size,
                fitness_fn    = lambda p: fitness_con_penalizacion(
                    p, heatmap, [], dist_min, penal_max
                ),
                distancia_min = dist_min
            )
        else:
            pozos, poblacion = generar_pozos_aleatorios(
                n_pozos    = puntos,
                size       = size,
                fitness_fn = lambda p: fitness_con_penalizacion(
                    p, heatmap, [], dist_min, penal_max
                )
            )

        # Evolución
        for gen in range(generaciones):
            # Recalcular fitness y ordenar
            poblacion = [
                (pt, fitness_con_penalizacion(pt, heatmap, poblacion, dist_min, penal_max))
                for pt, _ in poblacion
            ]
            poblacion.sort(key=lambda x: x[1], reverse=True)

            # Selección
            if porc_sel < 100:
                n_sel = max(2, int(len(poblacion) * porc_sel / 100))
            else:
                n_sel = min(num_sel, len(poblacion))
            seleccionados = poblacion[:n_sel]

            # Cruce interno
            nuevos = cruce_interno_centro(
                seleccionados,
                size           = size,
                metodo         = cfg["metodo"],
                tipo_centro    = cfg["tipo_centro"],
                fitness_fn     = lambda p: fitness_con_penalizacion(
                    p, heatmap, seleccionados, dist_min, penal_max
                ),
                jitter         = jitter,
                peso_fitness   = 1.0,
                peso_distancia = 2.0,
                dist_min       = dist_min,
                penal_max      = penal_max
            )
            # Normalizar fitness en nuevos
            nuevos = [
                (pt, fitness_con_penalizacion(pt, heatmap, seleccionados, dist_min, penal_max))
                for pt, _ in nuevos
            ]

            # Preparar siguiente población
            candidatos = seleccionados + nuevos
            poblacion  = seleccionar_poblacion(
                candidatos,
                puntos    = puntos,
                elitismo  = cfg["elitismo"],
                aleatorio = cfg["aleatorio"]
            )

            # Guardar PNG
            mostrar_varios_conjuntos(
                [seleccionados, nuevos],
                size         = size,
                etiquetas    = ["Seleccionados", "Nuevos"],
                titulo       = f"{nombre} - Gen {gen}",
                heatmap      = heatmap,
                guardar_como = os.path.join(carpeta_imgs, f"generacion_{gen}.png")
            )

        # Guardar GIF final en /gif/<base>/<nombre>.gif
        salida_gif = os.path.join(gif_root, base, f"{nombre}.gif")
        os.makedirs(os.path.dirname(salida_gif), exist_ok=True)
        generar_gif(
            num_generaciones = generaciones,
            carpeta_imgs     = carpeta_imgs,
            nombre_salida    = salida_gif,
            duracion         = 400
        )

    print(f"✅ Ejecutado {config_path}")
    print(f"– Imágenes en: {img_root}/{base}/...")
    print(f"– GIFs en:     {gif_root}/{base}/...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ejecuta escenarios desde un JSON y agrupa outputs en /img y /gif"
    )
    parser.add_argument(
        "config",
        help="Ruta al JSON de escenarios"
    )
    args = parser.parse_args()
    main(args.config)
