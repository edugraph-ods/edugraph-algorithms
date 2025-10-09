# EduGraph Algoritmos

Este repositorio contiene una implementación de algoritmos para resolver problemas relacionados con la planificación académica utilizando grafos y programación dinámica con máscaras (bitmasking). Además de documentar el enfoque y los conceptos aplicados.

## Escenario del problema

Supongamos que tengo una malla académica pequeña:

- Curso A -> prerrequisitos: ninguno -> 3 créditos
- Curso B -> prerequisitos: A -> 4 créditos
- Curso C -> prerrequisitos: A -> 2 créditos
- Curso D -> prerequisitos: B y C -> 5 créditos

Además de los cursos, tengo las siguientes restricciones:

- Máximo de 7 créditos por ciclo.
- El estado de un curso puede ser: "**aprobado**" o "**reprobado**".
- Si un curso esta desaprobado, se repite el en el siguente ciclo -> esto alarga el tiempo para terminar la carrera.


## Obejtivo

Calcular el **minímo número de ciclos** que necesita un estudiante para aprobar todos los cursos, considerando:
- Límite de créditos por ciclo.
- Dependencias en los cursos (prerrequisitos).
- Casos de desaprobación.

## Algoritmos utilizados

### 1. Representación como un grafo dirigido acíclico (DAG)

- Nodos = Cursos
- Aristas Dirigidas = Prerrequisitos
- Ejemplo: A -> B, A -> C, (B,C) -> D
Esto permite hacer un algoritmo de orden topológico para determinar el orden de los cursos.


Para este paso usamos DFS (Depth First Search/Busqueda en profundidad).
- Detecta si existe ciclos en la malla (caso inválido).
- Genera orden topológico de los cursos, que luego guía la planificación.
- Ejemplo de recorrido: ['A','C','B','D']


### 2. Definir el estado de un curso (Programación Dinámica con máscaras)

Cada estado debe reflejar qué cursos ya fueron desaprobados.
- Lo representamos con un bitmask (máscara de bits).
- 0000 = ningún curso aprobado
- 1000 = Un curso aprobado
- 1111 = todos los cursos aprobados

La máscara sirve para "**recordar**" el conjunto de cursos que ya fueron aprobados -> aquí se usa la memoización.

**Nota: El número de bits aumenta dependiendo la cantidad de cursos que llevo en cada ciclo**

### 3. Función de la Programación dinámica

Definimos la siguiente función:

`dp(mask) = mínimo número de ciclos necesarios desde este estado hasta terminar.`

1. Identidicamos los cursos disponibles en este estado (prerrequisitos cumplidos y no aprobado aún).
2. Agrupamos cursos disponibles respetando el límite de crédito por ciclo.
3. Para cada combinación:
- Actualizar la máscara (bitmask) con los cursos aprobados.
- Avanzar al siguiente ciclo.
- Tomar el mínimo entre todas las combinaciones.

Casos especiales:

- Si todos los cursos están aprobados: (mas=1111) -> dp(mask) = 0
- Si no hay cursos disponibles -> estado inválido
- Si un curso fue desaprobado, su bit no cambia y se repite en el próximo ciclo.

### 4. Uso de la Memoización

El espacio de estados puede crecer. Por ejemplo, con 'n' cursos, existen 2^n estados.

Para evitar el recalculo de los estados, aplicamos la **memoización**.
- Guardamos en una tabla o diccionario los resultados ya calculados de **'dp(mask)'**
- Si volvemos a un mismo estado, simplemente recuperamos el resultado almacenado.

Ejemplo:
- **dp(1111)**: 0 (todos aprobados)
- **dp(1010)**: mínimo de ciclos desde el estado donde el curso A y C están aprobados.
- Una vez calculado **dp(1010)**, si volvemos a este mismo estado no lo resolvemos otra vez, sino que se obtiene directamente de la memoria.

### 5. Ejemplo de aplicación:

**Caso 1: Todos los cursos aprobados (7 créditos máximos por ciclo)**

- Ciclo 1: Llevo A (3 créditos) + C (2 créditos) = 5 <= 7 -> paso al siguente ciclo `dp(1010) = me faltan 2 ciclos`
- Ciclo 2: Llevo B (4 créditos) + D (5 créditos) = 9 
  -> se excede el máximo de créditos, solo llevo B -> `dp(1110) = me falta 1 ciclo`
- Ciclo 3: Llevo D (4 créditos) -> `dp(1111) = 0 ciclos`

Tiempo total: 3 ciclos.

**Caso 2: Desapruebo C en ciclo 1**
- Ciclo 1: Llevo A(3) + C(2), pero desapruebo C -> `dp(1000) = me faltan 2 ciclos (solo A aprobado)`
- Ciclo 2: Llevo B(4) + C(2) = 6 <= 7 -> `dp(1110) = me falta 1 ciclo`
- Ciclo 3: Llevo D(4) -> `dp(1111) = 0 ciclos`

Tiempo total: 3 ciclos (igual que antes porque recuperé C en el ciclo 2).


**Caso 3: Desapruebo B en ciclo 2**
- Ciclo 1: A(3) + C(2) -> `dp(1010) = me faltan 2 ciclos`
- Ciclo 2: Llevo B(4) pero desapruebo el curso -> `dp(1010) = me faltan 2 ciclos`
- Ciclo 3: vuelvo a llevar B(4), pero ahora si lo apruebo -> `dp(1110) = me falta 1 ciclo`
- Ciclo 4: Llevo D(4) -> `Estado = 1111`

Tiempo total: 4 ciclos.


### Conceptos aplicados

1. DFS (orden topológico):
    - Recorrido del grafo para detectar ciclos y generar una secuencia válida de cursos.
    - Se puede visualizar el paso a paso del recorrido.
2. Programación dinámica con bitmasking:
    - Cada estado es un conjunto de cursos aprobados.
    - Se minimiza el número de ciclos mediante transiciones entre estados.
3. Memoización:
    - Optimiza el cálculo evitando los estados repetidos. 


### Conclusiones

La combinación de DFS y DP con bitmasking permite:

- Detectar dependencias y ciclos en la malla académica.

- Optimizar la selección de cursos por ciclo respetando límites de créditos.

- Calcular de forma eficiente el mínimo número de ciclos necesarios para completar la malla, incluso considerando desaprobaciones.

### Bibliotecas

- NetworkX: para la representación y análisis de grafos.

```
pip install networkx
```

- Matplotlib: para la visualización de grafos.

```
pip install matplotlib
```
