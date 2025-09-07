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
    Admite métodos cercanos, secuencial, ruleta y ruleta_dist, y centros geométrico o de masa.
    """
    # 1) Asegurar fitness en todos los individuos
    coords_con_fit = []
    for c in coords:
        if isinstance(c, tuple) and isinstance(c[0], tuple):
            pt, ft = c
            ft = float(ft) if ft is not None else 0.0
        else:
            pt = c
            ft = float(fitness_fn(pt)) if fitness_fn else 0.0
        coords_con_fit.append((pt, ft))

    nuevos = []
    n = len(coords_con_fit)

    # 2) Cruce principal
    for i, (p1, f1) in enumerate(coords_con_fit):
        # 2.1) Selección de pareja
        if metodo == "cercano":
            pareja = min(
                (coords_con_fit[j] for j in range(n) if j != i),
                key=lambda pf: distancia(p1, pf[0])
            )
        elif metodo == "secuencial":
            pareja = coords_con_fit[(i + 1) % n]
        elif metodo == "ruleta":
            pool = [(p, f) for j,(p,f) in enumerate(coords_con_fit) if j != i]
            pesos = [max(f,1e-6)**peso_fitness for _,f in pool]
            pareja = random.choices(pool, weights=pesos, k=1)[0]
        elif metodo == "ruleta_dist":
            pool = [(p, f) for j,(p,f) in enumerate(coords_con_fit) if j != i]
            pesos = []
            for p2, f2 in pool:
                d = distancia(p1, p2)
                factor = (1.0/(1.0+d))**peso_distancia
                pesos.append((max(f2,1e-6)**peso_fitness) * factor)
            pareja = random.choices(pool, weights=pesos, k=1)[0]
        else:
            raise ValueError(f"Método desconocido: {metodo}")

        p2, f2 = pareja

        # 2.2) Cálculo de centro
        if tipo_centro == "geometrico":
            xm = (p1[0] + p2[0]) / 2.0
            ym = (p1[1] + p2[1]) / 2.0
        elif tipo_centro == "masa":
            den = f1 + f2
            if abs(den) < 1e-8:
                # Caída al promedio geométrico
                xm = (p1[0] + p2[0]) / 2.0
                ym = (p1[1] + p2[1]) / 2.0
            else:
                xm = (p1[0]*f1 + p2[0]*f2) / den
                ym = (p1[1]*f1 + p2[1]*f2) / den
        else:
            raise ValueError(f"Tipo de centro desconocido: {tipo_centro}")

        # 2.3) Aplicar jitter (solo una vez)
        if jitter > 0:
            xm += random.uniform(-jitter, jitter)
            ym += random.uniform(-jitter, jitter)

        # 2.4) Asegurar coordenadas enteras y dentro de [0, size-1]
        xi = max(0, min(size - 1, int(round(xm))))
        yi = max(0, min(size - 1, int(round(ym))))
        pt_final = (xi, yi)
        ft_final = float(fitness_fn(pt_final)) if fitness_fn else None

        if ft_final is not None:
            nuevos.append((pt_final, ft_final))
        else:
            nuevos.append(pt_final)

    # 3) Fusión por penalización (opcional)
    if dist_min is not None and penal_max is not None and fitness_fn:
        combinados = []
        usados = set()
        for i, (p1, f1) in enumerate(nuevos):
            if i in usados:
                continue
            merged = False
            for j, (p2, f2) in enumerate(nuevos):
                if j <= i or j in usados:
                    continue
                d = distancia(p1, p2)
                penal = penal_max * max(0.0, 1.0 - d/dist_min)
                if penal >= penal_max:
                    # mismo cálculo de centro robusto
                    den = f1 + f2
                    if abs(den) < 1e-8:
                        xm = (p1[0] + p2[0]) / 2.0
                        ym = (p1[1] + p2[1]) / 2.0
                    else:
                        xm = (p1[0]*f1 + p2[0]*f2) / den
                        ym = (p1[1]*f1 + p2[1]*f2) / den

                    xi = max(0, min(size - 1, int(round(xm))))
                    yi = max(0, min(size - 1, int(round(ym))))
                    ft_new = float(fitness_fn((xi, yi)))
                    combinados.append(((xi, yi), ft_new))
                    usados.update([i, j])
                    merged = True
                    break
            if not merged:
                combinados.append((p1, f1))
                usados.add(i)
        nuevos = combinados

    return nuevos