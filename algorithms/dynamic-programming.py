from functools import lru_cache
from itertools import combinations
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

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

def visualizar_grafo(cursos, cursos_por_semestre):
    G = nx.DiGraph()
    
    # Mapeo de colores según el estado
    color_map = {
        'APROBADO': 'green',
        'DESAPROBADO': 'red',
        'NO RINDIO': 'orange',
        None: 'gray'
    }
    
    # Recolectar todos los cursos únicos (incluyendo prerrequisitos)
    todos_los_cursos = {curso['nombre']: curso for curso in cursos}
    
    # Agregar nodos con atributos
    for curso in cursos:
        G.add_node(curso['nombre'], 
                  creditos=curso['creditos'],
                  estado=curso['estado'],
                  semestre=curso.get('semestre', 0) + 1)
    
    # Agregar aristas (prerrequisitos)
    for curso in cursos:
        for prereq in curso['prereqs']:
            if prereq.lower() != 'ninguno':
                # Si el prerrequisito no está en los cursos, lo añadimos como nodo
                if prereq not in G:
                    G.add_node(prereq, 
                             creditos=0, 
                             estado='NO RINDIO',
                             semestre=0)  # Semestre 0 para cursos previos
                G.add_edge(prereq, curso['nombre'])
    
    # Configuración del gráfico
    plt.figure(figsize=(16, 12))
    
    # Crear un layout jerárquico para mejor visualización
    pos = {}
    
    # Primero posicionamos los cursos por semestre
    max_semestre = max([c.get('semestre', 0) for c in cursos] + [0])
    
    # Espacio vertical para los cursos por semestre
    y_offset = 0
    
    # Posicionar cursos por semestre
    for sem in range(max_semestre + 1):
        cursos_sem = [c['nombre'] for c in cursos if c.get('semestre', 0) == sem]
        if cursos_sem:
            y_offset = max(3, len(cursos_sem))  # Mínimo 3 de espacio vertical
            for i, curso in enumerate(cursos_sem):
                pos[curso] = (sem * 2, -i * (10.0 / y_offset))
    
    # Posicionar cursos previos (sin semestre) a la izquierda
    cursos_previos = [n for n in G.nodes() if n not in pos]
    if cursos_previos:
        y_offset = max(3, len(cursos_previos))
        for i, curso in enumerate(cursos_previos):
            pos[curso] = (-1, -i * (10.0 / y_offset))
    
    # Dibujar nodos
    for node in G.nodes():
        node_data = next((c for c in cursos if c['nombre'] == node), 
                        {'nombre': node, 'creditos': 0, 'estado': 'NO RINDIO'})
        
        # Dibujar nodo
        nx.draw_networkx_nodes(G, pos, nodelist=[node],
                             node_color=color_map.get(node_data.get('estado'), 'gray'),
                             node_size=2000,
                             node_shape='s',
                             alpha=0.8)
        
        # Etiqueta con nombre y créditos
        creditos = node_data.get('creditos', 0)
        label = f"{node}"
        if creditos > 0:
            label += f"\n({creditos} créditos)"
            
        plt.text(pos[node][0], pos[node][1], label, 
                ha='center', va='center',
                bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.3'))
    
    # Dibujar aristas
    nx.draw_networkx_edges(G, pos, 
                          edge_color='gray',
                          arrows=True,
                          arrowsize=15,
                          node_size=2000,
                          width=1.5,
                          connectionstyle='arc3,rad=0.1')  # Curvar las flechas
    
    # Añadir títulos y leyenda
    plt.title('Malla Curricular - Visualización de Cursos y Prerrequisitos\n', fontsize=14, pad=20)
    plt.suptitle('Semestres (izq → der) | Código de colores: Verde=Aprobado, Rojo=Desaprobado, Naranja=No rindió, Gris=Sin estado\n', 
                fontsize=9, y=0.97, color='#555555')
    
    # Leyenda mejorada
    legend_elements = [
        Patch(facecolor='green', label='Aprobado'),
        Patch(facecolor='red', label='Desaprobado'),
        Patch(facecolor='orange', label='No rindió'),
        Patch(facecolor='gray', label='Sin estado')
    ]
    
    plt.legend(handles=legend_elements, 
              loc='upper right', 
              bbox_to_anchor=(1.0, 1.0),
              title="Estado del curso")
    
    # Ajustar márgenes y mostrar
    plt.margins(0.2)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def main():
    print("=== Simulación de planificación académica con DFS + DP (bitmask) ===")
    cursos, cursos_por_semestre, max_creditos = leer_malla()
    asignar_estado_cursos(cursos_por_semestre)
    
    # Visualizar el grafo
    visualizar_grafo(cursos, cursos_por_semestre)
    
    # Continuar con la planificación si se desea
    continuar = input("¿Desea continuar con la planificación? (s/n): ").strip().lower()
    if continuar == 's':
        orden_topologico = dfs_topologico(cursos)
        planificar_ciclos(orden_topologico, max_creditos)

if __name__ == "__main__":
    main()
