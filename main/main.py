import math
from algoritmo import generar_pozos_aleatorios, cruce_interno_centro
from visualizacion import mostrar_varios_conjuntos
from generadorHeatMap import generar_heatmap

# =========================
# CONSTANTES GLOBALES
# =========================
TAMANO = 200
PUNTOS = 90
TIPO_DE_CENTRO = "masa"   # "masa" o "geometrico"
MAPA = "perlin"                  # "perlin", "random", "blobs", "distancia", etc.
METODO = "cercano"              # "cercano" o "secuencial"
ESCALA_PERLIN = 80.0
OCTAVAS_PERLIN = 3
GENERACIONES = 15

# Selección
PORCENTAJE_SELECCION = 100   # <100 → usa porcentaje, 100 → usa tamaño fijo
NUM_SELECCIONADOS = 30       # usado solo si PORCENTAJE_SELECCION == 100

# Parámetros de penalización
DISTANCIA_MIN = 1      # distancia mínima deseada entre puntos
PENALIZACION_MAX = 0.2 # penalización máxima por proximidad

# =========================
# FUNCIÓN DE FITNESS CON PENALIZACIÓN
# =========================
def fitness_con_penalizacion(p, heatmap, poblacion_existente, dist_min, penalizacion_max):
    base = heatmap[p[0], p[1]]
    penal = 0
    for q in poblacion_existente:
        q_point = q[0] if isinstance(q[0], tuple) else q
        dist = math.hypot(p[0] - q_point[0], p[1] - q_point[1])
        if dist < dist_min:
            penal += penalizacion_max * (1 - dist / dist_min)
    return base - penal

# =========================
# PROGRAMA PRINCIPAL
# =========================
if __name__ == "__main__":
    size = TAMANO
    puntos = PUNTOS
    tipo_centro = TIPO_DE_CENTRO
    metodo = METODO
    mapa = MAPA

    # Mapa de calor
    if mapa.lower() == "perlin":
        heatmap = generar_heatmap(size, tipo="perlin", escala=ESCALA_PERLIN, octavas=OCTAVAS_PERLIN)
    else:
        heatmap = generar_heatmap(size, tipo=mapa)

    # Población inicial
    poblacion = generar_pozos_aleatorios(
        puntos, size,
        fitness_fn=lambda p: fitness_con_penalizacion(p, heatmap, [], DISTANCIA_MIN, PENALIZACION_MAX)
    )

    for gen in range(GENERACIONES):
        # Recalcular fitness con penalización en base a la población actual
        poblacion = [(p[0], fitness_con_penalizacion(p[0], heatmap, poblacion, DISTANCIA_MIN, PENALIZACION_MAX))
                     for p in poblacion]

        # Ordenar por fitness
        poblacion.sort(key=lambda x: x[1], reverse=True)

        # Selección
        if PORCENTAJE_SELECCION < 100:
            n_sel = max(2, int(len(poblacion) * (PORCENTAJE_SELECCION / 100)))
        else:
            n_sel = min(NUM_SELECCIONADOS, len(poblacion))
        seleccionados = poblacion[:n_sel]

        # Reproducción con jitter
        nuevos = cruce_interno_centro(
            seleccionados,
            size=size,
            metodo=metodo,
            tipo_centro=tipo_centro,
            fitness_fn=lambda p: fitness_con_penalizacion(p, heatmap, seleccionados, DISTANCIA_MIN, PENALIZACION_MAX),
            jitter=1.5
        )

        # Evaluar fitness de nuevos con penalización
        nuevos = [(p[0], p[1]) if isinstance(p[0], tuple) else
                  (p, fitness_con_penalizacion(p, heatmap, seleccionados, DISTANCIA_MIN, PENALIZACION_MAX))
                  for p in nuevos]

        # Nueva población
        poblacion = (seleccionados + nuevos)[:puntos]

        # Visualización
        mostrar_varios_conjuntos(
            [seleccionados, nuevos],
            size=size,
            etiquetas=["Seleccionados", "Nuevos"],
            titulo=f"Generación {gen} con penalización por proximidad",
            heatmap=heatmap,
            guardar_como=f"./img/generacion_{gen}.png"
        )
