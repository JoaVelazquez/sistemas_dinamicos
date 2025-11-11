# 📚 Guía de Ejemplos Rápidos - Sistema de Simulaciones

## Resumen de Ejemplos Agregados

Se han agregado **botones de ejemplos rápidos** visibles y fáciles de usar a TODOS los simuladores del sistema.

---

## 🔴 1. Bifurcaciones 1D (`bifurcaciones_1.py`)

### Ejemplos Disponibles:

#### **Fila 1: Bifurcaciones Clásicas**
1. **Nodo Tangente** - `r² - x²`
   - Parámetros: r ∈ [-2, 2], x ∈ [-3, 3]
   - Valores fase: -1, 0, 1

2. **Transcrítica** - `rx - x²`
   - Parámetros: r ∈ [-2, 2], x ∈ [-3, 3]
   - Valores fase: -1, 0, 1

3. **Horca** - `r + x - ln(1+x)`
   - Parámetros: r ∈ [-1, 2], x ∈ [0.1, 3]
   - Valores fase: -0.5, 0, 0.5, 1

#### **Fila 2: Bifurcaciones Avanzadas**
4. **Supercrítica** - `r - x³`
   - Parámetros: r ∈ [-2, 2], x ∈ [-2, 2]
   - Valores fase: -1, 0, 1

5. **Subcrítica** - `r + x³`
   - Parámetros: r ∈ [-2, 2], x ∈ [-2, 2]
   - Valores fase: -1, 0, 1

6. **Logística** - `rx(1-x)`
   - Parámetros: r ∈ [0, 4], x ∈ [0, 1]
   - Valores fase: 0.5, 1, 2, 3

**Uso**: Click en cualquier botón para cargar automáticamente la función y parámetros óptimos.

---

## 🔵 2. Sistemas Lineales 2D (`sistemas_lineales_2d.py`)

### Ejemplos Disponibles:

#### **Fila 1: Comportamientos Básicos**
1. **Nodo Estable (Atractor)**
   - Matriz: A = [[-1, 0], [0, -2]]
   - Todas las trayectorias convergen al origen

2. **Nodo Inestable (Repulsor)**
   - Matriz: A = [[1, 0], [0, 2]]
   - Todas las trayectorias divergen del origen

3. **Espiral Estable (Sumidero)**
   - Matriz: A = [[-1, -2], [2, -1]]
   - Trayectorias espiralan hacia el origen

#### **Fila 2: Comportamientos Complejos**
4. **Espiral Inestable (Fuente)**
   - Matriz: A = [[1, 2], [-2, 1]]
   - Trayectorias espiralan alejándose del origen

5. **Centro (Órbitas)**
   - Matriz: A = [[0, -1], [1, 0]]
   - Órbitas cerradas alrededor del origen

6. **Punto Silla (Hiperbólico)**
   - Matriz: A = [[1, 0], [0, -1]]
   - Combinación de atracción y repulsión

**Uso**: Click en cualquier botón para cargar la matriz del sistema.

---

## 🟢 3. Simulador de Lanchester (`simulador_lanchester.py`)

### Ejemplos Disponibles:

#### **Conflictos Bélicos:**

1. **Batalla Equilibrada**
   - Blue: 100 tropas, α = 0.01
   - Red: 100 tropas, β = 0.01
   - Resultado: Empate técnico

2. **Superioridad Blue**
   - Blue: 150 tropas, α = 0.015
   - Red: 80 tropas, β = 0.008
   - Resultado: Victoria Blue clara

#### **Interacciones Ecológicas:**

3. **Competencia**
   - Especie 1: 50 individuos, r₁ = 0.01, K₁ = 200
   - Especie 2: 60 individuos, r₂ = 0.01, K₂ = 200
   - Interacción: Competencia mutua (a₁₂ = a₂₁ = 0.0002)

4. **Predador-Presa**
   - Presas: 40 individuos, r₁ = 0.8
   - Predadores: 15 individuos, r₂ = -0.3
   - Interacción: Lotka-Volterra clásica
   - Muestra ciclos de población

5. **Mutualismo**
   - Especie 1: 30 individuos, r₁ = 0.005, K₁ = 200
   - Especie 2: 30 individuos, r₂ = 0.005, K₂ = 200
   - Interacción: Mutualismo (a₁₂ = a₂₁ = 0.0001)
   - Ambas especies se benefician

**Uso**: Click en cualquier botón para cargar el escenario completo.

---

## 🟠 4. Bifurcación de Hopf (`bifurcacion_hopf.py`)

### Ejemplos Ya Existentes:

1. **Hopf Clásico**
   - Sistema: x' = μx - y - x(x²+y²), y' = x + μy - y(x²+y²)
   - Bifurcación en μ = 0

2. **Van der Pol**
   - Sistema: x' = y, y' = μ(1-x²)y - x
   - Oscilador no lineal clásico

---

## 🟣 5. Sistemas No Lineales 2D (`sistemas_no_lineales_2d.py`)

### Ejemplos Ya Existentes:

Sección "Ejercicios" con múltiples sistemas predefinidos:
- Péndulo simple
- Oscilador de Van der Pol
- Sistemas competitivos
- Sistemas de presa-predador
- Y muchos más...

---

## 🟢 6. Simulador de Verhulst (`simulador_verhulst.py`)

### Ejemplos Ya Existentes:

1. **COVID-19**
   - 7 puntos de datos (30 días)
   - N = 2000
   - Propagación rápida

2. **Gripe Estacional**
   - 7 puntos de datos (28 días)
   - N = 500
   - Propagación moderada

---

## 🎨 Diseño Consistente

Todos los botones de ejemplos tienen:
- ✅ **Colores temáticos** según el simulador
- ✅ **Texto descriptivo** en 2 líneas
- ✅ **Iconos** 📚 en los títulos
- ✅ **Hover effects** con colores más claros
- ✅ **Cursor de mano** al pasar sobre ellos
- ✅ **Fuente bold** para mejor legibilidad
- ✅ **Bordes raised** para efecto 3D

---

## 🚀 Cómo Usar

1. **Abre cualquier simulador**
2. **Busca la sección "📚 Ejemplos Rápidos"**
3. **Click en el ejemplo que quieras probar**
4. **Los parámetros se cargan automáticamente**
5. **Click en "Analizar" o "Simular" para ver resultados**

---

## 💡 Ventajas

- ⚡ **Inicio rápido**: No necesitas conocer los parámetros
- 📖 **Educativo**: Cada ejemplo muestra un comportamiento típico
- 🎯 **Validación**: Verifica que el simulador funcione correctamente
- 🔄 **Comparación**: Prueba diferentes casos fácilmente
- 🎓 **Aprendizaje**: Ideal para estudiantes y principiantes

---

## 📝 Notas Técnicas

### Implementación:
- Método `_create_quick_examples()` en cada simulador
- Métodos `_load_example_*()` para cargar datos
- Botones `tk.Button` con colores personalizados (mejor que ttk en Windows)
- Integración con variables `tk.Variable` existentes

### Ubicación:
- **Bifurcaciones 1D**: Antes de los botones de acción
- **Sistemas Lineales**: Antes de trayectorias interactivas
- **Lanchester**: Antes de los botones de acción
- **Otros**: Ya existentes, mejorados con el tiempo

---

¡Ahora todos los simuladores son más accesibles y fáciles de usar! 🎉
