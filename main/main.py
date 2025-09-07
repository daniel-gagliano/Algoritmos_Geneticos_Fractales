import os
import math
import random
from algoritmo import generar_pozos_aleatorios, generar_pozos_equidistantes, cruce_interno_centro
from visualizacion import mostrar_varios_conjuntos
from generadorHeatMap import generar_heatmap
from generarGif import generar_gif

# =========================
# CONSTANTES GLOBALES
# =========================
TAMANO = 1000
PUNTOS = 100
ESCALA_PERLIN = 700.0
OCTAVAS_PERLIN = 3
GENERACIONES = 50  # menos para pruebas rápidas
JITTER = 5

# Selección
PORCENTAJE_SELECCION = 100
NUM_SELECCIONADOS = 60

# Penalización
DISTANCIA_MIN = 2
PENALIZACION_MAX = 0.4

# =========================
# FUNCIÓN DE FITNESS CON PENALIZACIÓN
# =========================
def fitness_con_penalizacion(p, heatmap, poblacion_existente, dist_min, penalizacion_max):
    base = heatmap[p[0], p[1]]
    penal = 0
    for q in poblacion_existente:
        # q puede venir como (punto, fitness) o como punto directamente
        q_point = q[0] if isinstance(q[0], tuple) else q
        dist = math.hypot(p[0] - q_point[0], p[1] - q_point[1])
        if dist < dist_min:
            penal += penalizacion_max * (1 - dist / dist_min)
    return base - penal

# =========================
# GENERACIÓN DE POZOS
# =========================
def generar_pozos(puntos, size, fitness_fn, modo="aleatorio", distancia_min=None):
    if modo == "equidistante":
        # puntos aquí es cantidad de pozos
        return generar_pozos_equidistantes(
            num_pozos=puntos,
            grid_size=size,
            fitness_fn=fitness_fn,
            distancia_min=distancia_min
        )
    elif modo == "aleatorio":
        return generar_pozos_aleatorios(puntos, size, fitness_fn)
    else:
        raise ValueError(f"Modo de generación desconocido: {modo}")


# =========================
# SELECCIÓN PARAMETRIZADA
# =========================
def seleccionar_poblacion(candidatos, puntos, elitismo=0, aleatorio=True):
    candidatos_ordenados = sorted(candidatos, key=lambda x: x[1], reverse=True)
    mejores = candidatos_ordenados[:elitismo] if elitismo > 0 else []
    resto = candidatos_ordenados[elitismo:]
    if aleatorio:
        pesos = [max(f, 0.0001) for _, f in resto]
        seleccionados_resto = random.choices(resto, weights=pesos, k=puntos - len(mejores))
    else:
        seleccionados_resto = resto[:puntos - len(mejores)]
    return mejores + seleccionados_resto

# =========================
# ESCENARIOS A EJECUTAR
# =========================
escenarios = [
    {
        "nombre": "ruleta_dist_elit",
        "mapa": "blobs",
        "mapa_params": {
            "num_blobs": 80,
            "radio_min": 40,
            "radio_max": 160
        },
        "metodo": "ruleta_dist",
        "tipo_centro": "masa",
        "elitismo": 10,
        "aleatorio": False,
        "modo": "equidistante"
    },
    {
        "nombre": "perlin_base",
        "mapa": "perlin",
        "mapa_params": {
            "escala": ESCALA_PERLIN,
            "octavas": OCTAVAS_PERLIN
        },
        "metodo": "ruleta_dist",
        "tipo_centro": "masa",
        "elitismo": 10,
        "aleatorio": False,
        "modo": "aleatorio"
    }
]

# =========================
# BUCLE PRINCIPAL MULTI-GIF
# =========================
if __name__ == "__main__":
    size = TAMANO
    puntos = PUNTOS

    for cfg in escenarios:
        carpeta_imgs = f"./img/{cfg['nombre']}"
        os.makedirs(carpeta_imgs, exist_ok=True)

        # Generar mapa de calor
        heatmap = generar_heatmap(
            size,
            tipo=cfg["mapa"],
            **cfg.get("mapa_params", {})
        )

        pozos, poblacion = generar_pozos(
            puntos, size,
            fitness_fn=lambda p: fitness_con_penalizacion(p, heatmap, [], DISTANCIA_MIN, PENALIZACION_MAX),
            modo=cfg.get("modo", "aleatorio"),
            distancia_min=DISTANCIA_MIN
        )

        for gen in range(GENERACIONES):
            # Recalcular fitness de la población actual
            poblacion = [
                (p[0], fitness_con_penalizacion(p[0], heatmap, poblacion, DISTANCIA_MIN, PENALIZACION_MAX))
                for p in poblacion
            ]

            # Ordenar y seleccionar
            poblacion.sort(key=lambda x: x[1], reverse=True)
            if PORCENTAJE_SELECCION < 100:
                n_sel = max(2, int(len(poblacion) * (PORCENTAJE_SELECCION / 100)))
            else:
                n_sel = min(NUM_SELECCIONADOS, len(poblacion))
            seleccionados = poblacion[:n_sel]

            # Reproducción mediante cruce interno
            nuevos = cruce_interno_centro(
                seleccionados,
                size=size,
                metodo=cfg["metodo"],
                tipo_centro=cfg["tipo_centro"],
                fitness_fn=lambda p: fitness_con_penalizacion(p, heatmap, seleccionados, DISTANCIA_MIN, PENALIZACION_MAX),
                jitter=JITTER,
                peso_fitness=1.0,
                peso_distancia=2.0,
                dist_min=DISTANCIA_MIN,
                penal_max=PENALIZACION_MAX
            )

            # Evaluar fitness de los nuevos
            nuevos = [
                (p[0], p[1]) if isinstance(p[0], tuple)
                else (p, fitness_con_penalizacion(p, heatmap, seleccionados, DISTANCIA_MIN, PENALIZACION_MAX))
                for p in nuevos
            ]

            # Unir y seleccionar la siguiente generación
            candidatos = seleccionados + nuevos
            poblacion = seleccionar_poblacion(
                candidatos,
                puntos=puntos,
                elitismo=cfg["elitismo"],
                aleatorio=cfg["aleatorio"]
            )

            # Guardar imagen de esta generación
            mostrar_varios_conjuntos(
                [seleccionados, nuevos],
                size=size,
                etiquetas=["Seleccionados", "Nuevos"],
                titulo=f"{cfg['nombre']} - Gen {gen}",
                heatmap=heatmap,
                guardar_como=f"{carpeta_imgs}/generacion_{gen}.png"
            )

        # Generar el GIF para este escenario
        generar_gif(GENERACIONES, carpeta_imgs, f"{cfg['nombre']}.gif")
