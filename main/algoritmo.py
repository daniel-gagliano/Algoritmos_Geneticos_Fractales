import random
import math

def generar_pozos_aleatorios(n_pozos, size, fitness_fn=None):
    """
    Genera coordenadas (x, y) únicas de pozos de forma aleatoria.
    Si se pasa fitness_fn, devuelve [(punto, fitness), ...]
    """
    if n_pozos > size * size:
        raise ValueError("Más pozos que celdas disponibles.")

    coords = set()
    while len(coords) < n_pozos:
        coords.add((random.randint(0, size - 1), random.randint(0, size - 1)))
    
    coords = list(coords)
    if fitness_fn:
        return [(p, fitness_fn(p)) for p in coords]
    return coords

def distancia(p1, p2):
    """Distancia euclidiana entre dos puntos."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def cruce_interno_centro(coords, size, metodo="cercano", tipo_centro="geometrico", fitness_fn=None, jitter=0):
    """
    Genera nuevos puntos como el centro entre pares de puntos, con opción de jitter.
    
    - metodo: "cercano" o "secuencial"
    - tipo_centro: "geometrico" o "masa"
    - coords: puede ser [(punto, fitness), ...] o [(x, y), ...]
    - fitness_fn: si coords no trae fitness, se calcula aquí
    - jitter: desplazamiento aleatorio máximo en celdas (entero)
    """
    nuevos = []

    for i, p1 in enumerate(coords):
        # Extraer punto y fitness si viene en formato extendido
        if isinstance(p1, tuple) and isinstance(p1[0], tuple):
            punto1, fit1 = p1
        else:
            punto1 = p1
            fit1 = fitness_fn(p1) if fitness_fn else 1

        # Selección del compañero
        if metodo == "cercano":
            candidato = min(
                (p for j, p in enumerate(coords) if j != i),
                key=lambda p: distancia(punto1, p[0] if isinstance(p, tuple) and isinstance(p[0], tuple) else p)
            )
        elif metodo == "secuencial":
            candidato = coords[(i + 1) % len(coords)]
        else:
            raise ValueError("Método no reconocido")

        # Extraer punto y fitness del compañero
        if isinstance(candidato, tuple) and isinstance(candidato[0], tuple):
            punto2, fit2 = candidato
        else:
            punto2 = candidato
            fit2 = fitness_fn(punto2) if fitness_fn else 1

        # Calcular centro
        if tipo_centro == "geometrico":
            xm = (punto1[0] + punto2[0]) / 2
            ym = (punto1[1] + punto2[1]) / 2
        elif tipo_centro == "masa":
            xm = (punto1[0] * fit1 + punto2[0] * fit2) / (fit1 + fit2)
            ym = (punto1[1] * fit1 + punto2[1] * fit2) / (fit1 + fit2)
        else:
            raise ValueError("Tipo de centro no reconocido")

        # Aplicar jitter si corresponde
        if jitter > 0:
            xm += random.uniform(-jitter, jitter)
            ym += random.uniform(-jitter, jitter)

        # Ajustar a la grilla
        xi = max(0, min(size - 1, int(round(xm))))
        yi = max(0, min(size - 1, int(round(ym))))

        punto_final = (xi, yi)
        fit_final = fitness_fn(punto_final) if fitness_fn else None

        nuevos.append((punto_final, fit_final) if fit_final is not None else punto_final)

    return nuevos
