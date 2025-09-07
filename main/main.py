import os
import math
import random

from algoritmo import (
    generar_pozos_aleatorios,
    generar_pozos_equidistantes,
    cruce_interno_centro,
    seleccionar_poblacion
)
from visualizacion import mostrar_varios_conjuntos
from cargarHeatMap import cargar_heatmap
from generarGif import generar_gif

# =========================
# ESCENARIOS A EJECUTAR
# =========================
escenarios = [
    {
        "nombre": "aleatorio_random",
        "metodo": "ruleta_dist",
        "tipo_centro": "masa",
        "elitismo": 10,
        "aleatorio": False,
        "modo": "aleatorio",
        "puntos": 100,
        "generaciones": 50,
        "jitter": 5,
        "porcentaje_seleccion": 100,
        "num_seleccionados": 60,
        "distancia_min": 2,
        "penalizacion_max": 0.4
    },
    {
        "nombre": "distancia_centro_distancia_suave",
        "metodo": "ruleta_dist",
        "tipo_centro": "masa",
        "elitismo": 10,
        "aleatorio": False,
        "modo": "aleatorio",
        "puntos": 100,
        "generaciones": 50,
        "jitter": 5,
        "porcentaje_seleccion": 100,
        "num_seleccionados": 60,
        "distancia_min": 2,
        "penalizacion_max": 0.4
    },
    {
        "nombre": "grad_horizontal_gradiente",
        "metodo": "ruleta_dist",
        "tipo_centro": "masa",
        "elitismo": 10,
        "aleatorio": False,
        "modo": "aleatorio",
        "puntos": 100,
        "generaciones": 50,
        "jitter": 5,
        "porcentaje_seleccion": 100,
        "num_seleccionados": 60,
        "distancia_min": 2,
        "penalizacion_max": 0.4
    },
    {
        "nombre": "manchas_grand_blobs",
        "metodo": "ruleta_dist",
        "tipo_centro": "masa",
        "elitismo": 10,
        "aleatorio": False,
        "modo": "aleatorio",
        "puntos": 100,
        "generaciones": 50,
        "jitter": 5,
        "porcentaje_seleccion": 100,
        "num_seleccionados": 60,
        "distancia_min": 2,
        "penalizacion_max": 0.4
    },
    {
        "nombre": "manchas_med_blobs",
        "metodo": "ruleta_dist",
        "tipo_centro": "masa",
        "elitismo": 10,
        "aleatorio": False,
        "modo": "aleatorio",
        "puntos": 100,
        "generaciones": 50,
        "jitter": 5,
        "porcentaje_seleccion": 100,
        "num_seleccionados": 60,
        "distancia_min": 2,
        "penalizacion_max": 0.4
    },
    {
        "nombre": "manchas_peq_blobs",
        "metodo": "ruleta_dist",
        "tipo_centro": "masa",
        "elitismo": 10,
        "aleatorio": False,
        "modo": "aleatorio",
        "puntos": 100,
        "generaciones": 50,
        "jitter": 5,
        "porcentaje_seleccion": 100,
        "num_seleccionados": 60,
        "distancia_min": 2,
        "penalizacion_max": 0.4
    },
    {
        "nombre": "perlin_fina_perlin",
        "metodo": "ruleta_dist",
        "tipo_centro": "masa",
        "elitismo": 10,
        "aleatorio": False,
        "modo": "aleatorio",
        "puntos": 100,
        "generaciones": 50,
        "jitter": 5,
        "porcentaje_seleccion": 100,
        "num_seleccionados": 60,
        "distancia_min": 2,
        "penalizacion_max": 0.4
    },
    {
        "nombre": "perlin_gruesa_perlin",
        "metodo": "ruleta_dist",
        "tipo_centro": "masa",
        "elitismo": 10,
        "aleatorio": False,
        "modo": "aleatorio",
        "puntos": 100,
        "generaciones": 50,
        "jitter": 5,
        "porcentaje_seleccion": 100,
        "num_seleccionados": 60,
        "distancia_min": 2,
        "penalizacion_max": 0.4
    }
]

def fitness_con_penalizacion(p, heatmap, poblacion, dist_min, penal_max):
    base = heatmap[p[0], p[1]]
    penal = 0
    for q in poblacion:
        q_pt = q[0] if isinstance(q[0], tuple) else q
        d = math.hypot(p[0] - q_pt[0], p[1] - q_pt[1])
        if d < dist_min:
            penal += penal_max * (1 - d / dist_min)
    return base - penal

if __name__ == "__main__":
    for cfg in escenarios:
        nombre    = cfg["nombre"]
        carpeta   = f"./img/{nombre}"
        os.makedirs(carpeta, exist_ok=True)

        heatmap = cargar_heatmap(nombre)
        size    = heatmap.shape[0]

        puntos      = cfg["puntos"]
        generaciones= cfg["generaciones"]
        jitter      = cfg["jitter"]
        porc_sel    = cfg["porcentaje_seleccion"]
        num_sel     = cfg["num_seleccionados"]
        dist_min    = cfg["distancia_min"]
        penal_max   = cfg["penalizacion_max"]

        # -> Llamada explícita según modo
        if cfg["modo"] == "equidistante":
            pozos, poblacion = generar_pozos_equidistantes(
                num_pozos=puntos,
                grid_size=size,
                fitness_fn=lambda p: fitness_con_penalizacion(
                    p, heatmap, [], dist_min, penal_max
                ),
                distancia_min=dist_min
            )
        else:
            pozos, poblacion = generar_pozos_aleatorios(
                n_pozos=puntos,
                size=size,
                fitness_fn=lambda p: fitness_con_penalizacion(
                    p, heatmap, [], dist_min, penal_max
                )
            )

        for gen in range(generaciones):
            poblacion = [
                (p[0], fitness_con_penalizacion(
                    p[0], heatmap, poblacion, dist_min, penal_max
                ))
                for p in poblacion
            ]

            poblacion.sort(key=lambda x: x[1], reverse=True)

            if porc_sel < 100:
                n_sel = max(2, int(len(poblacion) * porc_sel / 100))
            else:
                n_sel = min(num_sel, len(poblacion))
            seleccionados = poblacion[:n_sel]

            nuevos = cruce_interno_centro(
                seleccionados,
                size=size,
                metodo=cfg["metodo"],
                tipo_centro=cfg["tipo_centro"],
                fitness_fn=lambda p: fitness_con_penalizacion(
                    p, heatmap, seleccionados, dist_min, penal_max
                ),
                jitter=jitter,
                peso_fitness=1.0,
                peso_distancia=2.0,
                dist_min=dist_min,
                penal_max=penal_max
            )

            nuevos = [
                (p[0], p[1]) if isinstance(p[0], tuple)
                else (p, fitness_con_penalizacion(
                    p, heatmap, seleccionados, dist_min, penal_max
                ))
                for p in nuevos
            ]

            candidatos = seleccionados + nuevos
            poblacion  = seleccionar_poblacion(
                candidatos,
                puntos=puntos,
                elitismo=cfg["elitismo"],
                aleatorio=cfg["aleatorio"]
            )

            mostrar_varios_conjuntos(
                [seleccionados, nuevos],
                size=size,
                etiquetas=["Seleccionados", "Nuevos"],
                titulo=f"{nombre} - Gen {gen}",
                heatmap=heatmap,
                guardar_como=f"{carpeta}/generacion_{gen}.png"
            )

        generar_gif(generaciones, carpeta, f"{nombre}.gif")
