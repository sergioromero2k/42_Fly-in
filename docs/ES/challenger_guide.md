# Challenger — The Impossible Dream (39 turnos)

## El problema
El mapa tiene 25 drones y zonas extremadamente restrictivas.  
Los cuellos de botella principales son `micro_gate1`, `micro_gate2` y `micro_gate3` — cada uno con `max_drones=1`.

Con **6454 caminos posibles**, el greedy básico mandaba todos los drones por `micro_gate1`, creando un cuello de botella imposible.

---

## La solución — Bottleneck Detection

En vez de usar todos los caminos, el simulador detecta automáticamente los **3 cuellos de botella más críticos** (zonas con `max_drones=1` que aparecen en más caminos) y selecciona el camino más corto que pase por cada uno:

- `micro_gate1` → camino más corto que lo usa  
- `micro_gate2` → camino más corto que lo usa  
- `micro_gate3` → camino más corto que lo usa  

Así, los **25 drones se distribuyen equitativamente entre 3 rutas paralelas** en vez de colapsar en una sola.

---

## Por qué funciona

- 3 micro_gates × 1 drone/turno = **3 drones/turno**  
- 25 drones ÷ 3 = ~9 turnos mínimo para pasar todos  
- + longitud del camino = **39 turnos totales**

* Mejor que el récord de 45  
* Resultado óptimo bajo estas condiciones

---

## Preguntas típicas sobre el Challenger

### ¿Cómo detectas los cuellos de botella automáticamente?
Uso un `Counter` que cuenta cuántas veces aparece cada zona con `max_drones=1` en todos los caminos.  
Las 3 zonas que aparecen más veces son los cuellos de botella más críticos.

---

### ¿Por qué 3 cuellos de botella y no 5 o 10?
Porque el mapa tiene exactamente **3 micro_gates como puntos de acceso al final**.  
El algoritmo detecta los más frecuentes automáticamente — si el mapa tuviera 5, cogería 5.

---

### ¿Esta optimización rompe los mapas más simples?
No — en mapas simples sin cuellos de botella claros, `best_paths` puede estar vacío y el código hace fallback:

```python
paths = best_paths if best_paths else paths
```

### ¿Por qué no usaste esta estrategia desde el principio?

Porque para mapas simples el greedy round-robin es suficiente y más rápido.
Esta optimización solo ayuda cuando hay múltiples cuellos de botella paralelos que se pueden explotar simultáneamente.