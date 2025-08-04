import numpy as np
import matplotlib.pyplot as plt
import random
import csv

def generar_mapa_fractal(tamaño, escala_inicial):
    mapa = np.zeros((tamaño, tamaño))

    valor_inicial = random.uniform(0.4, 0.6)
    mapa[0, 0] = mapa[0, -1] = mapa[-1, 0] = mapa[-1, -1] = valor_inicial

    paso = tamaño - 1
    escala = escala_inicial

    while paso > 1:
        mitad = paso // 2

        # Paso "diamante"
        for x in range(0, tamaño - 1, paso):
            for y in range(0, tamaño - 1, paso):
                centro_x = x + mitad
                centro_y = y + mitad
                promedio = (mapa[x, y] + mapa[x+paso, y] + mapa[x, y+paso] + mapa[x+paso, y+paso]) / 4.0
                mapa[centro_x, centro_y] = promedio + random.uniform(-escala, escala)

        # Paso "cuadrado"
        for x in range(0, tamaño, mitad):
            for y in range((x + mitad) % paso, tamaño, paso):
                total = 0
                contador = 0

                for dx, dy in [(-mitad, 0), (mitad, 0), (0, -mitad), (0, mitad)]:
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < tamaño and 0 <= ny < tamaño:
                        total += mapa[nx, ny]
                        contador += 1

                promedio = total / contador if contador > 0 else 0
                mapa[x, y] = promedio + random.uniform(-escala, escala)

        paso = mitad
        escala = escala / 2.0

    return np.clip(mapa, 0, 1)

def aplicar_mascara_geologica_simple(mapa):
    tamaño = mapa.shape[0]

    x = np.linspace(-1, 1, tamaño)
    y = np.linspace(-1, 1, tamaño)
    X, Y = np.meshgrid(x, y)

    centro = np.exp(-(X**2 + Y**2) / 0.5)
    fractura = np.exp(-((X + Y)**2) / 0.2)

    mascara_total = 0.7 * centro + 0.3 * fractura

    mapa_modificado = mapa * mascara_total

    return np.clip(mapa_modificado, 0, 1)

# Parámetros
SIZE = 33
MAPA = generar_mapa_fractal(SIZE, 0.5)
MAPA = aplicar_mascara_geologica_simple(MAPA)
N_POZOS = 10
POBLACION = 50
GENERACIONES = 60
PROB_CROSSOVER = 0.75
PROB_MUTACION = 0.05

def guardar_resultados_csv(nombre_archivo, generacion, min_fit, max_fit, prom_fit, mejor_ind):
    modo = 'a' if generacion > 0 else 'w'
    with open(nombre_archivo, modo, newline='') as archivo:
        writer = csv.writer(archivo)
        if generacion == 0:
            writer.writerow(['Generación', 'Fitness Mínimo', 'Fitness Máximo', 'Fitness Promedio', 'Mejor Individuo'])
        writer.writerow([
            generacion,
            round(min_fit, 4),
            round(max_fit, 4),
            round(prom_fit, 4),
            str(mejor_ind)
        ])

def crear_individuo():
    return [ (random.randint(0, SIZE-1), random.randint(0, SIZE-1)) for _ in range(N_POZOS) ]

def fitness(ind):
    return sum([MAPA[x][y] for x,y in ind])

def cruce(p1, p2):
    if random.random() < PROB_CROSSOVER:
        corte = random.randint(1, N_POZOS-1)
        return p1[:corte] + p2[corte:]
    else:
        return p1.copy()

def mutar(ind):
    nuevo = []
    for gen in ind:
        if random.random() < PROB_MUTACION:
            nuevo.append((random.randint(0, SIZE-1), random.randint(0, SIZE-1)))
        else:
            nuevo.append(gen)
    return nuevo

def seleccion_torneo(poblacion, k=3):
    participantes = random.sample(poblacion, k)
    mejor = max(participantes, key=fitness)
    return mejor

# Inicialización
poblacion = [crear_individuo() for _ in range(POBLACION)]

for gen in range(GENERACIONES):
    poblacion = sorted(poblacion, key=fitness, reverse=True)

    fitness_vals = [fitness(ind) for ind in poblacion]
    max_fit = max(fitness_vals)
    min_fit = min(fitness_vals)
    prom_fit = sum(fitness_vals) / len(fitness_vals)
    mejor_ind = poblacion[0]

    guardar_resultados_csv("resultados_generaciones.csv", gen, min_fit, max_fit, prom_fit, mejor_ind)

    # Evolución sin elitismo, con torneo
    nueva = []
    while len(nueva) < POBLACION:
        padre1 = seleccion_torneo(poblacion)
        padre2 = seleccion_torneo(poblacion)
        hijo = mutar(cruce(padre1, padre2))
        nueva.append(hijo)
    poblacion = nueva

# Visualización
plt.figure(figsize=(7,7))
plt.imshow(MAPA, cmap='viridis')
plt.title('Mapa fractal geológico simulado con pozos óptimos')
for x, y in mejor_ind:
    plt.plot(y, x, 'ro')
plt.colorbar(label='Concentración relativa de litio')
plt.axis('off')
plt.show()

# Estimación de Litio Extraído
volumen = 500_000  # m³ por celda
densidad = 1200    # kg/m³
ley = 300 / 1_000_000  # ppm a fracción
recuperacion = 0.5

total_litio = 0
for x, y in mejor_ind:
    fraccion = MAPA[x][y]
    litio = volumen * densidad * (fraccion * ley) * recuperacion / 1_000_000
    total_litio += litio

print(f"Litio total estimado extraíble: {total_litio:.3f} toneladas")
