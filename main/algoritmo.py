import random
import math
import numpy as np

def generar_pozos_aleatorios(n_pozos, size, fitness_fn=None):
    """
    Genera n_pozos coordenadas únicas de forma aleatoria.
    Devuelve (pozos, poblacion), donde:
      - pozos = [(x,y), ...]
      - poblacion = [( (x,y), fitness ), ...]
    """
    if n_pozos > size * size:
        raise ValueError("Más pozos que celdas disponibles.")

    coords = set()
    while len(coords) < n_pozos:
        coords.add((random.randint(0, size - 1),
                    random.randint(0, size - 1)))
    coords = list(coords)

    # Si no hay fitness_fn, asumimos fitness = None
    if fitness_fn:
        poblacion = [(p, fitness_fn(p)) for p in coords]
    else:
        poblacion = [(p, None) for p in coords]

    pozos = [p for p, _ in poblacion]
    return pozos, poblacion


def generar_pozos_equidistantes(num_pozos, grid_size, fitness_fn, distancia_min=None):
    """
    num_pozos: cantidad de pozos a generar
    grid_size: dimensión del mapa (asumimos cuadrado de [0..grid_size-1]^2)
    fitness_fn: función que recibe un punto (tupla int,int) y devuelve su fitness
    distancia_min: si es None, se calcula automáticamente según la rejilla
    """
    # límites del dominio
    x_min, x_max = 0, grid_size - 1
    y_min, y_max = 0, grid_size - 1

    # cuántas columnas y filas necesitamos
    cols = int(np.ceil(np.sqrt(num_pozos)))
    rows = int(np.ceil(num_pozos / cols))

    # espaciado si no se pasa distancia_min
    if distancia_min is None:
        dx = (x_max - x_min) / (cols + 1)
        dy = (y_max - y_min) / (rows + 1)
    else:
        dx = dy = distancia_min

    # generar coordenadas flotantes equidistantes
    x_vals = np.linspace(x_min + dx, x_max - dx, cols)
    y_vals = np.linspace(y_min + dy, y_max - dy, rows)

    # formar la rejilla y convertir a enteros
    grid = [(int(round(x)), int(round(y))) for y in y_vals for x in x_vals]

    # recortar a num_pozos
    pozos = grid[:num_pozos]

    # calcular fitness
    poblacion = [(p, fitness_fn(p)) for p in pozos]

    return pozos, poblacion

def distancia(p1, p2):
    """Distancia euclidiana entre dos puntos."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

import random
import math

def distancia(p1, p2):
    """Distancia euclidiana entre dos puntos."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def cruce_interno_centro(
    coords, size,
    metodo="cercano",
    tipo_centro="masa",
    fitness_fn=None,
    jitter=0,
    peso_fitness=1.0,
    peso_distancia=1.0,
    dist_min=None,
    penal_max=None
):
    """
    Genera nuevos puntos como el centro entre pares de puntos, con opción de jitter.
    Integra combinación de puntos demasiado cercanos con penalización máxima.

    - metodo: "cercano", "secuencial", "ruleta", "ruleta_dist"
    - tipo_centro: "geometrico" o "masa"
    - coords: puede ser [(punto, fitness), ...] o [(x, y), ...]
    - fitness_fn: si coords no trae fitness, se calcula aquí
    - jitter: desplazamiento aleatorio máximo en celdas (entero)
    - peso_fitness: exponente para ponderar la importancia del fitness (ruleta)
    - peso_distancia: exponente para ponderar la importancia de la distancia (ruleta_dist)
    - dist_min: distancia mínima para combinación (usa la misma que penalización)
    - penal_max: penalización máxima para combinación
    """
    nuevos = []

    # Asegurar que todos tengan fitness
    coords_con_fit = []
    for c in coords:
        if isinstance(c, tuple) and isinstance(c[0], tuple):
            coords_con_fit.append(c)
        else:
            coords_con_fit.append((c, fitness_fn(c) if fitness_fn else 1))

    for i, (punto1, fit1) in enumerate(coords_con_fit):

        # Selección del compañero
        if metodo == "cercano":
            candidato = min(
                (p for j, p in enumerate(coords_con_fit) if j != i),
                key=lambda p: distancia(punto1, p[0])
            )

        elif metodo == "secuencial":
            candidato = coords_con_fit[(i + 1) % len(coords_con_fit)]

        elif metodo == "ruleta":
            candidatos = [p for j, p in enumerate(coords_con_fit) if j != i]
            pesos = [max(f, 0.0001) ** peso_fitness for _, f in candidatos]
            candidato = random.choices(candidatos, weights=pesos, k=1)[0]

        elif metodo == "ruleta_dist":
            candidatos = [p for j, p in enumerate(coords_con_fit) if j != i]
            pesos = []
            for punto_cand, fit_cand in candidatos:
                dist = distancia(punto1, punto_cand)
                factor_distancia = 1 / (1 + dist)  # favorece cercanos
                peso = (max(fit_cand, 0.0001) ** peso_fitness) * (factor_distancia ** peso_distancia)
                pesos.append(peso)
            candidato = random.choices(candidatos, weights=pesos, k=1)[0]

        else:
            raise ValueError("Método no reconocido")

        punto2, fit2 = candidato

        # Calcular centro
        if tipo_centro == "geometrico":
            xm = (punto1[0] + punto2[0]) / 2
            ym = (punto1[1] + punto2[1]) / 2
        elif tipo_centro == "masa":
            xm = (punto1[0] * fit1 + punto2[0] * fit2) / (fit1 + fit2)
            ym = (punto1[1] * fit1 + punto2[1] * fit2) / (fit1 + fit2)
        else:
            raise ValueError("Tipo de centro no reconocido")

        # Aplicar jitter
        if jitter > 0:
            xm += random.uniform(-jitter, jitter)
            ym += random.uniform(-jitter, jitter)

        # Ajustar a la grilla
        xi = max(0, min(size - 1, int(round(xm))))
        yi = max(0, min(size - 1, int(round(ym))))

        punto_final = (xi, yi)
        fit_final = fitness_fn(punto_final) if fitness_fn else None

        nuevos.append((punto_final, fit_final) if fit_final is not None else punto_final)

    # --- Combinación de puntos cercanos con penalización máxima ---
    if dist_min is not None and penal_max is not None and fitness_fn is not None:
        usados = set()
        combinados = []
        for i, (pi, fi) in enumerate(nuevos):
            if i in usados:
                continue
            combinado = False
            for j, (pj, fj) in enumerate(nuevos):
                if j <= i or j in usados:
                    continue
                dist = distancia(pi, pj)
                penal = penal_max * max(0, 1 - dist / dist_min)
                if penal >= penal_max:
                    # Fusionar en centro de masa
                    xm = (pi[0] * fi + pj[0] * fj) / (fi + fj)
                    ym = (pi[1] * fi + pj[1] * fj) / (fi + fj)
                    xi = max(0, min(size - 1, int(round(xm))))
                    yi = max(0, min(size - 1, int(round(ym))))
                    nuevo_punto = (xi, yi)
                    nuevo_fit = fitness_fn(nuevo_punto)
                    combinados.append((nuevo_punto, nuevo_fit))
                    usados.update([i, j])
                    combinado = True
                    break
            if not combinado:
                combinados.append((pi, fi))
                usados.add(i)
        nuevos = combinados

    return nuevos
