# Guía de Uso - Simulador de Verhulst

## 🎯 Modos de Operación

### 1️⃣ **Modo Manual** (Predeterminado)
Ingresas todos los parámetros manualmente:
- **k**: Constante de propagación
- **N**: Población límite
- **P₀**: Población inicial infectada

**Uso**: Cuando ya conoces todos los parámetros del modelo.

---

### 2️⃣ **Modo: Resolver k desde 2 puntos** ✨ NUEVO
Calculas **k** automáticamente usando solo 2 observaciones.

**Requisitos**:
- ✅ Exactamente **2 puntos** de datos (día, infectados)
- ✅ Valor de **N** (población límite)
- ✅ Valor de **P₀** (población inicial)

**Pasos**:
1. ✅ Marca: "Resolver k desde 2 puntos"
2. 📊 Ingresa **N** (ej: 1000 personas)
3. 📊 Ingresa **P₀** (ej: 10 infectados iniciales)
4. ➕ Agrega **Punto 1**: día y número de infectados (ej: día 5, 50 infectados)
5. ➕ Agrega **Punto 2**: día y número de infectados (ej: día 10, 150 infectados)
6. 🧮 Click en "Simular Propagación"

**Fórmula**:
```
k = ln[(N-P₁)/P₁ / (N-P₂)/P₂] / [N(t₂-t₁)]
```

**Ejemplo Práctico**:
- Día 5: 50 infectados
- Día 10: 150 infectados  
- N = 1000
- P₀ = 10

→ El sistema calcula automáticamente k ≈ 0.000182

---

### 3️⃣ **Modo: Ajuste Automático**
Ajusta **k y N** usando múltiples puntos de datos (≥3).

**Uso**: 
1. ✅ Marca: "Ajustar k y N automáticamente"
2. ➕ Agrega varios puntos de datos (mínimo 3)
3. 🧮 Click en "Simular Propagación"

El sistema usa **mínimos cuadrados** para encontrar los mejores valores de k y N.

---

## 📊 Ejemplos Rápidos

### COVID-19
- Datos de 7 días
- N = 2000
- Propagación rápida

### Gripe Estacional
- Datos de 4 semanas
- N = 500
- Propagación moderada

---

## 🎨 Visualizaciones

1. **Gráfico Principal**: Población infectada vs tiempo
   - Línea azul: Solución analítica
   - Línea roja punteada: Solución numérica
   - Puntos verdes: Datos observados
   - Línea gris: Límite N
   - Línea naranja: Punto de inflexión (N/2)

2. **Diagrama de Fase**: Tasa de cambio vs población
   - Muestra cómo cambia la velocidad de propagación

3. **Velocidad de Propagación**: dP/dt vs tiempo
   - Muestra cuándo es máxima la velocidad de contagio

---

## 📝 Notas Importantes

⚠️ **Modo 2 Puntos**:
- Los 2 puntos deben mostrar **crecimiento** (P₂ > P₁)
- Ambos puntos deben ser **menores que N**
- Si el primer punto es t=0, se usará como P₀ automáticamente

⚠️ **Validación**:
- k debe ser **positivo** (crecimiento)
- P₀ < N (inicial menor que límite)
- Todos los valores deben ser **positivos**

---

## 🔬 Interpretación de Resultados

### Parámetro k
- **k pequeño** (ej: 0.0001): Propagación lenta
- **k grande** (ej: 0.001): Propagación rápida

### Punto de Inflexión (N/2)
- Momento de **máxima velocidad de propagación**
- Después de este punto, la propagación se desacelera

### Límite N
- Población máxima que puede infectarse
- Asíntota horizontal del modelo

---

## 💡 Tips

1. **Para epidemias reales**: Usa datos de los primeros días cuando el crecimiento es exponencial
2. **Para predecir**: Asegúrate de que N sea realista (población total susceptible)
3. **Para verificar**: Los puntos verdes deben estar cerca de la curva azul

---

¡Experimenta con diferentes valores y observa cómo cambia la dinámica de propagación! 🦠📈
