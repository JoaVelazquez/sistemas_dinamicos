# 🎯 Sistemas Dinámicos - Suite de Simulación Interactiva

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange.svg)](https://docs.python.org/3/library/tkinter.html)

Una suite completa de herramientas interactivas para el análisis y visualización de sistemas dinámicos lineales y no lineales.

[Características](#-características) • [Instalación](#-instalación) • [Uso](#-uso) • [Simuladores](#-simuladores) • [Ejemplos](#-ejemplos)

</div>

---

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Características](#-características)
- [Requisitos del Sistema](#-requisitos-del-sistema)
- [Instalación](#-instalación)
- [Uso Rápido](#-uso-rápido)
- [Simuladores Disponibles](#-simuladores-disponibles)
- [Guía de Uso Detallada](#-guía-de-uso-detallada)
- [Ejemplos](#-ejemplos)
- [Troubleshooting](#-troubleshooting)
- [Contribuir](#-contribuir)

---

## 🌟 Descripción General

Este proyecto proporciona una suite integrada de simuladores para el estudio de **sistemas dinámicos** en el contexto de modelado y simulación matemática. Incluye herramientas para:

- Análisis de bifurcaciones unidimensionales
- Bifurcaciones de Hopf
- Sistemas lineales 2D
- Sistemas no lineales 2D
- Simulaciones de Lanchester (guerra y ecología)
- Modelo de Verhulst para propagación epidemiológica

Todas las herramientas cuentan con **interfaz gráfica**, **visualizaciones interactivas** y **ejemplos predefinidos**.

---

## ✨ Características

- 🎨 **Interfaz Gráfica Intuitiva**: Diseñada con Tkinter para facilidad de uso
- 📊 **Visualizaciones en Tiempo Real**: Gráficos interactivos con Matplotlib
- 🧮 **Análisis Matemático Completo**: Autovalores, autovectores, clasificación de puntos críticos
- 📚 **Ejemplos Predefinidos**: Casos de estudio listos para ejecutar
- 💾 **Exportación de Datos**: Guarda resultados en CSV
- 🎯 **Interactividad**: Haz clic en gráficos para explorar trayectorias
- 🔬 **Rigor Matemático**: Soluciones analíticas y numéricas
- 📈 **Múltiples Modos de Análisis**: Desde simples a complejos

---

## 💻 Requisitos del Sistema

### Software

- **Python 3.8 o superior**
- **Sistema Operativo**: Windows, macOS, Linux

### Bibliotecas Python

```txt
numpy>=1.20.0
matplotlib>=3.3.0
scipy>=1.6.0
sympy>=1.8.0
tkinter (incluido con Python)
```

---

## 🚀 Instalación

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/JoaVelazquez/sistemas_dinamicos.git
cd sistemas_dinamicos/segunda_parte
```

### Paso 2: Instalar Dependencias

**Opción A: Usando pip**
```bash
pip install numpy matplotlib scipy sympy
```

**Opción B: Usando requirements.txt** (si existe)
```bash
pip install -r requirements.txt
```

### Paso 3: Verificar Instalación

```bash
python -c "import numpy, matplotlib, scipy, sympy, tkinter; print('✅ Todas las dependencias instaladas correctamente')"
```

---

## 🎮 Uso Rápido

### Lanzar la Suite Completa

```bash
python simulaciones.py
```

Esto abrirá el **launcher principal** con acceso a todos los simuladores.

### Ejecutar Simuladores Individuales

```bash
# Bifurcaciones 1D
python bifurcaciones_1.py

# Bifurcaciones de Hopf
python bifurcacion_hopf.py

# Sistemas Lineales 2D
python sistemas_lineales_2d.py

# Sistemas No Lineales 2D
python sistemas_no_lineales_2d.py

# Simulador de Lanchester
python simulador_lanchester.py

# Simulador de Verhulst (Epidemias)
python simulador_verhulst.py
```

---

## 🎯 Simuladores Disponibles

### 1. 🔴 Bifurcaciones 1D

Análisis de bifurcaciones en sistemas unidimensionales.

**Características:**
- Análisis de puntos de equilibrio
- Detección de bifurcaciones
- Diagramas de bifurcación
- Campos vectoriales

**Casos de estudio:**
- Bifurcación de silla-nodo
- Bifurcación transcrítica
- Bifurcación de horquilla (pitchfork)

### 2. 🟠 Bifurcaciones de Hopf

Simulador especializado para bifurcaciones de Hopf en sistemas 2D.

**Características:**
- Entrada de ecuaciones personalizadas
- Análisis paramétrico (μ₁, μ₂, μ₃)
- Retratos de fase comparativos
- Ejemplos clásicos (Van der Pol, Hopf estándar)

**Uso:**
```python
# Ejemplo: Sistema de Hopf
x' = μ*x - y - x*(x² + y²)
y' = x + μ*y - y*(x² + y²)
```

### 3. 🔵 Sistemas Lineales 2D

Análisis completo de sistemas lineales x' = Ax.

**Características:**
- Clasificación automática del punto crítico
- Cálculo de autovalores y autovectores
- Retrato de fase con campo vectorial
- Trayectorias interactivas (clic en gráfico)
- 6 ejemplos predefinidos

**Tipos de puntos críticos:**
- ✅ Nodo estable/inestable
- ✅ Silla de montar
- ✅ Centro (órbitas cerradas)
- ✅ Espiral estable/inestable

**Ejemplos rápidos:**
- Nodo estable: `A = [[-1, 0], [0, -1]]`
- Silla: `A = [[1, 0], [0, -1]]`
- Centro: `A = [[0, -1], [1, 0]]`

### 4. 🟣 Sistemas No Lineales 2D

Análisis de sistemas no lineales generales.

**Características:**
- Entrada de ecuaciones simbólicas
- Análisis de isoclinas
- Puntos críticos y linealización
- Retrato de fase con trayectorias
- Ejemplos: Lotka-Volterra, Van der Pol, Péndulo

**Uso:**
```python
# Ejemplo: Sistema Lotka-Volterra
x' = x*(2-y)
y' = y*(x-1)
```

### 5. 🟢 Simulador de Lanchester

Modelo de Lanchester para combate y ecología.

**Modos:**
1. **Combate clásico**: Dos fuerzas en conflicto
2. **Interacciones ecológicas**:
   - Competencia
   - Predador-Presa (Lotka-Volterra)
   - Mutualismo

**Características:**
- Predicción de resultados
- Análisis temporal
- Múltiples escenarios

### 6. 🟢 Modelo de Verhulst (Epidemias)

Simulador de propagación epidemiológica con el modelo logístico.

**Características:**
- **3 modos de operación**:
  1. Manual: Ingresa k, N, P₀
  2. Resolver k desde 2 puntos
  3. Ajuste automático (mínimos cuadrados)

- Ejemplos: COVID-19, Gripe estacional
- Exportar datos a CSV
- Simulación visual de contagio
- Análisis paso a paso

**Ecuación:**
```
dP/dt = k·P·(N-P)
Solución: P(t) = N/(1 + C·e^(-k·N·t))
```

---

## 📖 Guía de Uso Detallada

### Usando el Launcher Principal

1. **Ejecutar**: `python simulaciones.py`
2. Verás **6 tarjetas** de colores, una por simulador
3. **Haz clic** en la tarjeta deseada
4. Se abrirá el simulador en una nueva ventana

### Flujo de Trabajo Típico

#### Para Sistemas Lineales 2D:

```
1. Cargar ejemplo rápido → "Espiral estable"
2. Observar clasificación automática
3. Ver autovalores y autovectores
4. Hacer clic en el gráfico para trayectorias
5. Modificar matriz A manualmente
6. Analizar nuevamente
```

#### Para Verhulst (Epidemias):

**Modo 1: Con 2 puntos de datos**
```
1. Marcar "Resolver k desde 2 puntos"
2. Ingresar N = 1000 (población límite)
3. Ingresar P₀ = 10 (infectados iniciales)
4. Agregar punto 1: día 5, infectados 50
5. Agregar punto 2: día 10, infectados 150
6. Click "Simular Propagación"
→ k se calcula automáticamente
```

**Modo 2: Ajuste automático**
```
1. Marcar "Ajustar k y N automáticamente"
2. Cargar ejemplo "COVID-19"
3. Click "Simular Propagación"
→ k y N se ajustan por mínimos cuadrados
```

#### Para Bifurcaciones de Hopf:

```
1. Seleccionar ejemplo "Hopf clásico"
2. Ver 3 retratos de fase (μ₁, μ₂, μ₃)
3. Modificar valores de μ
4. Ingresar ecuaciones personalizadas
5. Analizar bifurcación
```

---

## 💡 Ejemplos

### Ejemplo 1: Analizar un Nodo Inestable

**Sistemas Lineales 2D**

```python
# Matriz A
A = [[1, 0],
     [0, 1]]

# Resultado esperado:
# - Clasificación: Nodo inestable (repulsor)
# - Autovalores: λ₁ = 1, λ₂ = 1
# - Trayectorias divergen del origen
```

### Ejemplo 2: Modelar Propagación de Gripe

**Verhulst**

```python
# Datos observados
Día 0:  5 infectados
Día 3:  25 infectados
Día 7:  95 infectados
Día 10: 200 infectados

# Parámetros
N = 500  # Población total
P₀ = 5   # Inicial

# Usar "Ajuste automático" para calcular k
# Predecir: ¿Cuántos en día 20?
```

### Ejemplo 3: Espiral Estable

**Sistemas Lineales 2D**

```python
# Matriz A
A = [[-1, -1],
     [ 1, -1]]

# Resultado:
# - Autovalores complejos: -1 ± i
# - Espiral estable
# - Trayectorias convergen en espiral al origen
```

### Ejemplo 4: Sistema Predador-Presa

**Lanchester (modo ecológico)**

```python
# Seleccionar: "Predador-Presa"
Presas iniciales (x₀): 100
Predadores iniciales (y₀): 20

# Observar oscilaciones periódicas
```

---

## 🐛 Troubleshooting

### Problema: No se abre la ventana gráfica

**Solución:**
```bash
# Verificar tkinter
python -c "import tkinter; tkinter.Tk()"

# Si falla en Linux:
sudo apt-get install python3-tk
```

### Problema: Error de importación de módulos

**Solución:**
```bash
# Reinstalar dependencias
pip uninstall numpy matplotlib scipy sympy
pip install numpy matplotlib scipy sympy --upgrade
```

### Problema: Gráficos no se actualizan

**Solución:**
- Click en "🧹 Limpiar" antes de analizar nuevo sistema
- Reiniciar el simulador
- Verificar que los valores ingresados sean numéricos válidos

### Problema: k negativo en Verhulst

**Causa:** Los puntos de datos muestran decrecimiento o están mal ordenados

**Solución:**
- Verificar que P₂ > P₁ (crecimiento)
- Asegurar que P₁ < P₂ < N
- Los datos deben ser de la fase de crecimiento

### Problema: Trayectorias no visibles

**Solución:**
- Ajustar límites de gráfico (x_min, x_max, y_min, y_max)
- Aumentar tiempo máximo
- Verificar que la matriz A no tenga autovalores muy grandes

---

## 🎓 Casos de Uso Académicos

### Para Estudiantes

1. **Tarea sobre nodos y sillas**: Usar Sistemas Lineales 2D
2. **Proyecto de epidemiología**: Verhulst con datos reales
3. **Análisis de estabilidad**: Sistemas No Lineales 2D
4. **Bifurcaciones**: Hopf con parámetros variables

### Para Profesores

- Demostrar conceptos en clase
- Generar ejercicios variados
- Visualizar teoremas
- Comparar métodos analíticos vs numéricos

---

## 📊 Estructura del Proyecto

```
segunda_parte/
├── simulaciones.py              # 🚀 Launcher principal
├── bifurcaciones_1.py           # 🔴 Bifurcaciones 1D
├── bifurcacion_hopf.py          # 🟠 Bifurcaciones Hopf
├── sistemas_lineales_2d.py      # 🔵 Sistemas Lineales
├── sistemas_no_lineales_2d.py   # 🟣 Sistemas No Lineales
├── simulador_lanchester.py      # 🟢 Lanchester
├── simulador_verhulst.py        # 🟢 Verhulst/Epidemias
├── GUIA_VERHULST.md            # 📖 Guía detallada Verhulst
└── README.md                    # 📄 Este archivo
```

---

## 🔬 Fundamentos Matemáticos

### Sistemas Lineales

Un sistema lineal 2D tiene la forma:

$$\frac{dx}{dt} = a_{11}x + a_{12}y$$

$$\frac{dy}{dt} = a_{21}x + a_{22}y$$

O en forma matricial: $\mathbf{x}' = A\mathbf{x}$

**Clasificación según autovalores:**
- λ₁, λ₂ reales negativos → Nodo estable
- λ₁, λ₂ reales positivos → Nodo inestable
- λ₁, λ₂ reales de signo opuesto → Silla de montar
- λ = α ± βi, α < 0 → Espiral estable
- λ = α ± βi, α > 0 → Espiral inestable
- λ = ± βi (α = 0) → Centro

### Modelo de Verhulst

Ecuación logística:

$$\frac{dP}{dt} = kP(N-P)$$

**Solución analítica:**

$$P(t) = \frac{N}{1 + Ce^{-kNt}}$$

Donde $C = \frac{N-P_0}{P_0}$

**Cálculo de k desde 2 puntos:**

$$k = \frac{\ln\left[\frac{(N-P_1)/P_1}{(N-P_2)/P_2}\right]}{N(t_2-t_1)}$$

---

## 🤝 Contribuir

¿Encontraste un bug o tienes una sugerencia?

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

---

## 📞 Soporte

Para preguntas o problemas:

- **GitHub Issues**: [Crear issue](https://github.com/JoaVelazquez/sistemas_dinamicos/issues)
- **Email**: [Tu email]
- **Documentación adicional**: Ver `GUIA_VERHULST.md`

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 🙏 Agradecimientos

- Desarrollado para el curso de **Modelado y Simulación** en UADE
- Inspirado en ejemplos clásicos de sistemas dinámicos
- Bibliotecas: NumPy, Matplotlib, SciPy, SymPy

---

## 🚀 Próximas Características

- [ ] Exportación de gráficos a PNG/PDF
- [ ] Más ejemplos predefinidos
- [ ] Análisis de sistemas 3D
- [ ] Integración con Jupyter Notebooks
- [ ] Modo oscuro para la interfaz

---

<div align="center">

**⭐ Si te resultó útil, dale una estrella al repo ⭐**

[⬆ Volver arriba](#-sistemas-dinámicos---suite-de-simulación-interactiva)

</div>
