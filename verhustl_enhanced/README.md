Verhulst – Streamlit con simulación de agentes (mapa de contagio)
=================================================================

Requisitos
----------
- Python 3.9+
- Paquetes: streamlit, numpy, pandas, matplotlib

Instalación
-----------
pip install -r requirements.txt

Ejecución
---------
streamlit run streamlit_app.py

Secciones
---------
1) Derivación del modelo logístico, con fórmulas y sustitución numérica.
2) Simulación (RK4 vs Analítica) y descargas de CSV.
3) **Mapa de contagio (agentes)** con controles: cantidad de agentes, infectados iniciales,
   radio de contagio, probabilidad β, velocidad de movimiento, pasos, retardo entre frames,
   y opción de recuperación con tiempo configurable.

Controles
---------
- "Reiniciar agentes": crea una nueva población aleatoria según los parámetros.
- "Iniciar simulación": corre la animación durante la cantidad de pasos indicada.
