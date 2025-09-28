from functools import lru_cache
from itertools import combinations
from collections import defaultdict

def leer_malla():
    semestres = int(input("Número total de semestres: "))
    max_creditos = int(input("Máximo de créditos por semestre: "))
    cursos = []
    cursos_por_semestre = []

    for s in range(semestres):
        print(f"\n--- Semestre {s+1} ---")
        n = int(input(f"Número de cursos que vas a llevar en semestre {s+1}: "))
        semestre_actual = []
        for i in range(n):
            nombre = input(f"Curso {i+1} del semestre {s+1}: ").strip()
            creditos = int(input(f"Créditos de {nombre}: "))
            prereq_input = input(f"Prerrequisitos de {nombre} (separados por coma, sin espacios si hay): ").strip()
            prereqs = [p.strip() for p in prereq_input.split(",")] if prereq_input else []
            semestre_actual.append({
                'nombre': nombre,
                'creditos': creditos,
                'prereqs': prereqs,
                'estado': None,
                'semestre': s
            })
        cursos_por_semestre.append(semestre_actual)
        cursos.extend(semestre_actual)

    return cursos, cursos_por_semestre, max_creditos


def asignar_estado_cursos(cursos_por_semestre):
    aprobados = set()
    no_rindio = set()

    for s, semestre in enumerate(cursos_por_semestre):
        print(f"\n--- Estado de cursos semestre {s+1} ---")
        for curso in semestre:
            if any(p not in aprobados for p in curso['prereqs']):
                curso['estado'] = 'NO RINDIO'
                no_rindio.add(curso['nombre'])
            else:
                aprobado_input = input(f"{curso['nombre']} aprobado? (s/n): ").strip().lower()
                if aprobado_input == 's':
                    curso['estado'] = 'APROBADO'
                    aprobados.add(curso['nombre'])
                else:
                    curso['estado'] = 'DESAPROBADO'
                    no_rindio.add(curso['nombre'])

    print("\n--- Estado final de cursos ---")
    for semestre in cursos_por_semestre:
        for curso in semestre:
            print(f"{curso['nombre']}: {curso['estado']}")

    return cursos_por_semestre

def dfs_topologico(cursos):
    grafo = defaultdict(list)
    nombres = [c['nombre'] for c in cursos]

    for c in cursos:
        for p in c['prereqs']:
            grafo[p].append(c['nombre'])

    visitado, stack, orden = {}, {}, []

    def dfs(nodo):
        if nodo in stack:
            raise ValueError("Hay un ciclo en los prerequisitos.")
        if nodo in visitado:
            return
        stack[nodo] = True
        for vecino in grafo[nodo]:
            dfs(vecino)
        stack.pop(nodo)
        visitado[nodo] = True
        orden.append(nodo)

    for c in nombres:
        if c not in visitado:
            dfs(c)

    orden.reverse()
    print("\nOrden topológico (DFS de prerequisitos):", orden)
    return orden

def planificar_ciclos(cursos, max_creditos):
    n = len(cursos)
    index = {cursos[i]['nombre']: i for i in range(n)}

    mask_inicial = 0
    for i, c in enumerate(cursos):
        if c['estado'] == 'APROBADO':
            mask_inicial |= (1 << i)

    cursos_a_rendir = [i for i, c in enumerate(cursos) if c['estado'] != 'APROBADO']

    def prerequisitos_cumplidos(mask, idx):
        return all(mask & (1 << index[p]) for p in cursos[idx]['prereqs'])

    cursos_a_rendir.sort(key=lambda i: cursos[i]['semestre'])

    @lru_cache(None)
    def dp(mask):
        if mask == (1 << n) - 1:
            return 0

        disponibles = [i for i in cursos_a_rendir if not (mask & (1 << i)) and prerequisitos_cumplidos(mask, i)]
        if not disponibles:
            return float('inf')

        best = float('inf')
        for r in range(1, len(disponibles) + 1):
            for subset in combinations(disponibles, r):
                creditos = sum(cursos[i]['creditos'] for i in subset)
                if creditos <= max_creditos:
                    nuevo_mask = mask
                    for i in subset:
                        nuevo_mask |= (1 << i)
                    best = min(best, 1 + dp(nuevo_mask))
        return best

    resultado = dp(mask_inicial)
    if resultado == float('inf'):
        print("\nResultado: Imposible completar todos los cursos con los estados actuales.")
    else:
        print(f"\nResultado: Mínimo número de ciclos adicionales necesarios para nivelarte = {resultado}")


def main():
    cursos, cursos_por_semestre, max_creditos = leer_malla()
    cursos_por_semestre = asignar_estado_cursos(cursos_por_semestre)

    # Paso 1: DFS para validar prerequisitos
    try:
        dfs_topologico(cursos)
    except ValueError as e:
        print(e)
        return

    # Paso 2: DP con bitmask para planificación
    planificar_ciclos(cursos, max_creditos)

if __name__ == "__main__":
    print("=== Simulación de planificación académica con DFS + DP (bitmask) ===")
    main()
