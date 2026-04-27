# Fly-in — Guía de Estudio para la Peer Review

---

## De qué trata el proyecto

**Fly-in** es un sistema de enrutamiento de drones. Tienes un mapa con zonas conectadas entre sí (un grafo) y una flota de N drones que deben ir desde una zona de inicio (`start_hub`) hasta una zona final (`end_hub`) en el **mínimo número de turnos posible**, respetando:

- Capacidad máxima de cada zona (`max_drones`)
- Capacidad máxima de cada conexión (`max_link_capacity`)
- Tipos de zona: `normal`, `restricted`, `blocked`, `priority`
- Movimiento simultáneo de todos los drones

---

## Qué debe mostrar el output

```
Turn 1: D1-waypoint1 D2-corridorA
Turn 2: D1-waypoint2 D2-tunnelB
Turn 3: D1-goal D2-goal
Simulation complete!
Total turns: 3
Drones delivered: 2/2
```

- Cada línea = 1 turno
- `D<ID>-<zona>` = drone X se movió a zona Y
- Drones que no se mueven → no aparecen en esa línea
- Drones que llegan al goal → desaparecen del output
- Al final → resumen de turnos y drones entregados

---

## Algoritmos usados

### 1. Dijkstra — ruta óptima para un drone

Encuentra el camino de **menor coste** entre start y end.
Usa una cola de prioridad (`heapq`) que siempre expande el nodo más barato primero.

```
Costes por tipo de zona destino:
  normal    → 1 turno
  priority  → 1 turno (preferida en empate)
  restricted→ 2 turnos
  blocked   → infinito (inaccesible)
```

**Pasos del algoritmo:**
1. Inicializar distancias a infinito, start a 0
2. Meter `(0, start)` en la cola de prioridad
3. Sacar el nodo más barato
4. Si es el end → reconstruir camino con `previous`
5. Si ya visitado → ignorar
6. Para cada vecino → calcular nuevo coste y actualizar

**Complejidad:** `O((V + E) log V)` donde V = zonas, E = conexiones

---

### 2. DFS con Backtracking — todos los caminos posibles

Explora recursivamente todos los caminos entre start y end.
Cuando llega a un callejón o al goal, vuelve atrás (backtrack).

```
dfs(zona_actual, camino_actual, visitados):
    para cada vecino:
        si vecino == end → guardar camino
        si no visitado:
            añadir a camino y visitados
            dfs(vecino, ...)     ← recursión
            quitar de camino y visitados  ← backtrack
```

---

### 3. Greedy Scheduling — asignar drones a rutas

1. Encontrar todos los caminos con DFS
2. Ordenar por longitud (más cortos primero)
3. Filtrar caminos demasiado largos (`shortest + 2`)
4. Asignar cada drone al camino con **menos drones ya asignados**

---

## Estructura de carpetas — por qué así

Seguimos el principio de **separación de responsabilidades**:

```
models/     → representar los datos     (qué ES el mapa)
parser/     → leer y validar el archivo (cómo LEER el mapa)
pathfinder/ → encontrar rutas           (cómo NAVEGAR el mapa)
simulator/  → ejecutar la simulación    (cómo MOVER los drones)
visualizer/ → mostrar resultados        (cómo VER la simulación)
```

---

## Clases — qué hace cada una

### `Zone` — models/zone.py
Representa un **nodo del grafo** — una zona del mapa.
```
name        → identificador único
x, y        → coordenadas para visualización
zone_type   → normal/restricted/priority/blocked
color       → para visualización terminal y gráfica
max_drones  → cuántos drones pueden estar a la vez (default 1)
```

### `Connection` — models/connection.py
Representa una **arista bidireccional** entre dos zonas.
```
zone_a, zone_b      → las dos zonas conectadas
max_link_capacity   → drones que pueden cruzar simultáneamente (default 1)
```

### `Graph` — models/graph.py
Contiene **todo el mapa**.
```
zones       → lista de todas las Zone
connections → lista de todas las Connection
start       → zona de inicio
end         → zona final
nb_drones   → número de drones a routear
```

### `Parser` — parser/map_parser.py
Lee el archivo `.txt` y construye el `Graph`.
```
parse_zone(parts)  → crea una Zone desde una línea spliteada
parse(filepath)    → lee el archivo completo, devuelve Graph
```
Valida: tipos de zona, conexiones duplicadas, nb_drones positivo, start/end presentes.

### `PathFinder` — pathfinder/pathfinder.py
Encuentra rutas en el grafo.
```
get_neighbors(zone)        → zonas vecinas ignorando blocked
get_cost(zone)             → coste de entrar a una zona
find_path(start, end)      → Dijkstra, devuelve ruta óptima
find_all_paths(start, end) → DFS, devuelve TODAS las rutas válidas
dfs(...)                   → helper recursivo para find_all_paths
```

### `Drone` — simulator/drone.py
Representa un **drone individual** con su estado.
```
id           → identificador (1, 2, 3...)
current_zone → zona donde está ahora
path         → lista de zonas que debe recorrer
path_index   → en qué punto del camino va
state        → "waiting" / "arrived"
```

### `Simulator` — simulator/simulator.py
**Corazón del proyecto** — ejecuta la simulación turno a turno.
```
run()              → bucle principal hasta que todos lleguen
compute_turn()     → calcula movimientos de un turno
get_ocupation()    → cuenta drones por zona
can_move()         → comprueba si un drone puede entrar a una zona
```

### `TerminalVisualizer` — visualizer/terminal.py
Imprime cada turno con **colores ANSI** según el color de la zona.
```
get_color(zone_name)        → devuelve código ANSI del color
print_turn(turn, movements) → imprime turno con colores
```

### `GraphDisplay` — visualizer/graph_display.py
Muestra el **grafo gráficamente** con matplotlib antes de la simulación.
```
draw() → dibuja zonas en sus coordenadas x,y con sus colores,
         conexiones como líneas y nombres de zonas
```

---

## Cómo se relacionan entre sí

```
main.py
  → Parser.parse(filepath) → Graph
  → Simulator(Graph)
      → PathFinder.find_all_paths() → lista de rutas
      → Drone(id, start, ruta) × nb_drones
      → TerminalVisualizer(Graph)
      → GraphDisplay(Graph)
      → run()
          → GraphDisplay.draw()
          → compute_turn() por cada turno
              → get_ocupation()
              → can_move() por cada drone
          → TerminalVisualizer.print_turn()
          → resumen final
```

---

## Preguntas típicas de la peer review

### Sobre el proyecto en general

**Q: ¿Qué hace este proyecto en una frase?**
> Routea una flota de drones por un grafo de zonas desde un inicio hasta un destino en el mínimo número de turnos, respetando capacidades y tipos de zona.

**Q: ¿Por qué no usas networkx?**
> El enunciado prohíbe explícitamente cualquier librería que ayude con lógica de grafos (networkx, graphlib, etc.). Todo está implementado desde cero — Dijkstra, DFS, representación del grafo — para demostrar comprensión real de los algoritmos.

**Q: ¿Qué es un grafo no dirigido y por qué usas uno aquí?**
> Un grafo no dirigido tiene aristas bidireccionales — si existe conexión A-B, un drone puede ir de A→B y también de B→A. En este proyecto todas las conexiones son bidireccionales porque los drones pueden moverse en cualquier dirección.

---

### Sobre el algoritmo

**Q: Explícame Dijkstra paso a paso**
> 1. Inicializo distancias de todos los nodos a infinito, el start a 0
> 2. Meto `(0, start)` en una cola de prioridad (heapq)
> 3. Saco el nodo con menor coste acumulado
> 4. Si es el end, reconstruyo el camino con el diccionario `previous`
> 5. Marco el nodo como visitado para no procesarlo dos veces
> 6. Para cada vecino calculo nuevo coste y si es menor, lo actualizo
> 7. Repito hasta encontrar el end o agotar todos los nodos

**Q: ¿Cuál es la complejidad de tu Dijkstra?**
> `O((V + E) log V)` — V vértices (zonas) y E aristas (conexiones). El factor log V viene de las operaciones de inserción y extracción del heap.

**Q: ¿Por qué usas heapq y no una lista normal?**
> Heapq es una cola de prioridad — siempre devuelve el elemento de menor valor en O(log n). Con una lista normal tendría que buscar el mínimo en O(n) cada vez, haciendo el algoritmo mucho más lento.

**Q: ¿Qué devuelve find_path si no hay camino?**
> Devuelve una lista vacía `[]`. El Simulator detecta esto con `if not paths` y lanza un ValueError con mensaje claro.

**Q: ¿Qué diferencia hay entre find_path y find_all_paths?**
> `find_path` usa Dijkstra y devuelve UN solo camino óptimo. `find_all_paths` usa DFS con backtracking y devuelve TODOS los caminos válidos, lo que permite distribuir los drones en múltiples rutas simultáneas.

**Q: ¿Por qué necesitas DFS además de Dijkstra?**
> Dijkstra encuentra el camino más corto para un drone. Pero si todos los drones van por el mismo camino se bloquean en zonas con `max_drones=1`. Con DFS encuentro todos los caminos alternativos y distribuyo los drones para maximizar el paralelismo.

---

### Sobre la simulación

**Q: ¿Qué pasa si dos drones quieren entrar a la misma zona en el mismo turno?**
> El primero en procesarse entra y actualiza la ocupación. El segundo ve que la zona está llena (`ocupation.get(zone, 0) >= zone.max_drones`) y espera ese turno. No aparece en el output de ese turno.

**Q: Explica la regla "los drones que salen liberan capacidad ese mismo turno"**
> Cuando proceso un turno, primero calculo la ocupación inicial. Cuando un drone se mueve, actualizo inmediatamente la ocupación — el drone que sale libera su zona y el drone que entra ocupa la nueva. Así en el mismo turno, si D1 sale de zona A, D2 puede entrar a zona A sin esperar al siguiente turno.

**Q: ¿Cómo detectas que un drone ha llegado al goal?**
> Cuando `next_zone == self.graph.end`, el drone cambia su `state` a `"arrived"`. El bucle `while not all(drone.state == "arrived" for drone in self.drones)` termina cuando todos tienen ese estado.

**Q: ¿Qué es path_index y por qué no borras zonas de la lista?**
> `path_index` es un puntero al paso actual del drone en su ruta. En vez de borrar zonas de la lista (destructivo), simplemente avanzo el índice. Esto es más seguro y preserva el historial completo del camino.

---

### Sobre el parser

**Q: ¿Qué errores valida tu parser?**
> - Tipo de zona inválido (solo acepta normal, blocked, restricted, priority)
> - Conexión duplicada (a-b y b-a son lo mismo)
> - nb_drones <= 0
> - Zona referenciada en connection que no existe
> - Ausencia de start_hub o end_hub

**Q: ¿Cómo detectas conexiones duplicadas?**
> Uso un `set` de `frozenset` — `frozenset(["a","b"]) == frozenset(["b","a"])` es True porque frozenset no tiene orden. Así detecto que `hub-roof1` y `roof1-hub` son la misma conexión.

**Q: ¿Cómo parseas el metadata `[zone=restricted color=red]`?**
> Separo la línea con `split()`, cojo los elementos desde `parts[4:]`, limpio los corchetes con `replace()`, separo por `=` con `split("=")` y asigno según la clave (`zone`, `color`, `max_drones`).

---

### Sobre el OOP

**Q: ¿Por qué el proyecto es orientado a objetos?**
> Porque cada entidad del dominio tiene estado y comportamiento propios. Una `Zone` sabe su tipo y capacidad. Un `Drone` sabe dónde está y hacia dónde va. El `Simulator` orquesta todo. Separar en clases hace el código más mantenible, testeable y comprensible.

**Q: ¿Qué es un type hint y para qué sirve?**
> Es una anotación que indica el tipo esperado de un parámetro o variable, por ejemplo `def parse(self, filepath: str) -> Graph`. Python no las impone en runtime, pero mypy las verifica estáticamente y ayudan a detectar errores antes de ejecutar.

**Q: ¿Para qué sirve `__str__` en tus clases?**
> Para definir cómo se representa el objeto como string cuando haces `print(objeto)`. Sin él imprimiría algo como `<models.zone.Zone object at 0x7f...>`. Con él muestra información útil del objeto.

---

### Sobre la visualización

**Q: ¿Qué son los códigos ANSI?**
> Son secuencias de escape que el terminal interpreta como instrucciones de formato — colores, negrita, etc. Por ejemplo `\033[32m` activa el color verde y `\033[0m` lo resetea. Los uso para colorear el output de cada turno según el color de la zona destino.

**Q: ¿Por qué usas matplotlib y no otra librería?**
> Matplotlib es la librería estándar de Python para visualización/plotting. No tiene nada que ver con lógica de grafos — solo dibuja puntos y líneas. El enunciado solo prohíbe librerías de graph logic como networkx.

---

### Preguntas trampa

**Q: ¿Podrías añadir un nuevo tipo de zona llamado "turbo" que cueste 0 turnos?**
> Sí. Solo necesito añadir `"turbo"` a `VALID_ZONE_TYPES` en el parser y añadir el caso `if zone.zone_type == "turbo": return 0` en `get_cost` del PathFinder.

**Q: ¿Qué pasaría si nb_drones fuera 1000 en un mapa pequeño?**
> El programa funcionaría pero sería muy lento — muchos drones esperando en el start. El simulador lo manejaría correctamente respetando capacidades, pero el número de turnos sería muy alto.

**Q: ¿Qué hace `Optional[str]` en el type hint de color?**
> Indica que el atributo puede ser un `str` o `None`. Lo uso porque el color en el mapa es opcional — si no se especifica, `color` vale `None`.

**Q: ¿Por qué usas frozenset para detectar conexiones duplicadas y no un set normal?**
> Porque un set normal `{"a", "b"}` no es hashable y no puede meterse dentro de otro set. Un `frozenset` es inmutable y sí es hashable, por eso puede usarse como elemento de un set.

---

## Resultados de rendimiento

| Mapa | Drones | Target | Resultado | Estado |
|------|--------|--------|-----------|--------|
| Easy 1 — Linear path | 2 | ≤ 6 | 5 | ✅ |
| Easy 2 — Simple fork | 3 | ≤ 6 | 5 | ✅ |
| Easy 3 — Basic capacity | 4 | ≤ 8 | 5 | ✅ |
| Medium 1 — Dead end trap | 5 | ≤ 15 | 12 | ✅ |
| Medium 2 — Circular loop | 6 | ≤ 20 | 20 | ✅ |
| Medium 3 — Priority puzzle | 4 | ≤ 12 | 7 | ✅ |
| Hard 1 — Maze nightmare | 8 | ≤ 45 | 22 | ✅ |
| Hard 2 — Capacity hell | 12 | ≤ 60 | 33 | ✅ |
| Hard 3 — Ultimate challenge | 15 | ≤ 35 | 28 | ✅ |
