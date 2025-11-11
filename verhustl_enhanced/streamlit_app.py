# streamlit_app.py
import streamlit as st
import numpy as np
import pandas as pd
import math
import io
import time
import matplotlib.pyplot as plt

st.set_page_config(page_title="Verhulst – Simulador con pasos + Mapa de contagio", page_icon="🧮", layout="wide")

# ---------- Core math ----------
def f_rhs(t, P, k, N):
    return k * P * (N - P)

def rk4_step(f, t, y, h, k, N):
    k1 = f(t, y, k, N)
    k2 = f(t + h/2, y + h*k1/2, k, N)
    k3 = f(t + h/2, y + h*k2/2, k, N)
    k4 = f(t + h, y + h*k3, k, N)
    y_next = y + (h/6.0)*(k1 + 2*k2 + 2*k3 + k4)
    return y_next, k1, k2, k3, k4

def simulate_numeric(k, N, P0, tmax, dt, steps_to_log=10):
    t = 0.0
    P = float(P0)
    steps = int(max(1, math.ceil(tmax / dt)))
    times = [0.0]; values = [P]
    rk4_log = []
    for i in range(steps):
        P_next, k1, k2, k3, k4 = rk4_step(f_rhs, t, P, dt, k, N)
        P_next = max(0.0, min(N, P_next))
        if i < steps_to_log:
            rk4_log.append({
                "n": i, "t_n": t, "P_n": P,
                "k1": k1, "k2": k2, "k3": k3, "k4": k4, "P_(n+1)": P_next
            })
        t += dt
        P = P_next
        times.append(t); values.append(P)
    return np.array(times), np.array(values), pd.DataFrame(rk4_log)

def logistic_analytic(t, k, N, P0):
    if P0 <= 0:
        return 0.0
    denom = 1.0 + ((N - P0) / P0) * math.exp(-k * N * t)
    return N / denom

# ---------- Sidebar (inputs) ----------
st.sidebar.title("Parámetros")
k = st.sidebar.number_input("k (tasa de infección)", value=0.0001, min_value=0.0, step=0.0001, format="%.6f")
N = st.sidebar.number_input("N (población total)", value=10000.0, min_value=0.0, step=100.0)
P0 = st.sidebar.number_input("P(0) infectados iniciales", value=10.0, min_value=0.0, step=1.0)
tmax = st.sidebar.number_input("Tiempo máximo (días)", value=100.0, min_value=0.1, step=1.0)
dt = st.sidebar.number_input("Paso dt", value=0.1, min_value=0.001, step=0.1, format="%.3f")
t_eval = st.sidebar.number_input("Evaluar día t", value=30.0, min_value=0.0, step=1.0)

st.title("Modelo logístico de infección viral (Verhulst) – con pasos")
st.caption("Interfaz web en Streamlit (usa React por debajo). Incluye un mapa de contagio al final.")

# ---------- Section: Equation and derivation ----------
st.header("1) Ecuación y resolución paso a paso")
st.latex(r"\frac{dP}{dt} = k\,P\,(N-P)")

st.markdown("**Separación de variables**")
st.latex(r"\int \frac{1}{P(N-P)}\,dP = \int k\,dt")

st.markdown("**Fracciones simples**:")
st.latex(r"\frac{1}{P(N-P)} = \frac{1}{N}\left(\frac{1}{P} + \frac{1}{N-P}\right)")

st.markdown("**Integrando**:")
st.latex(r"\frac{1}{N}\left(\ln|P| - \ln|N-P|\right) = k\,t + C")

st.markdown("**Agrupando y exponenciando**:")
st.latex(r"\ln\!\left(\frac{P}{N-P}\right) = k\,N\,t + C' \quad\Rightarrow\quad \frac{P}{N-P} = C\,e^{kNt}")

st.markdown("**Condición inicial** $P(0)=P_0$")
st.latex(r"C = \frac{P_0}{N-P_0}")

st.markdown("**Solución**:")
st.latex(r"P(t) = \frac{N}{1 + \left(\frac{N-P_0}{P_0}\right)e^{-kNt}}")

C_val = (P0)/(N - P0) if N != P0 and N > 0 else float("inf")
A_val = (N - P0)/P0 if P0 > 0 else float("inf")
st.markdown("**Con tus parámetros:**")
st.latex(fr"C = \frac{{{P0}}}{{{N}-{P0}}} = {C_val:.6g}")
st.latex(fr"P(t) = \frac{{{N}}}{{1 + \left(\frac{{{N}-{P0}}}{{{P0}}}\right)e^{{-{k} \cdot {N}\, t}}}} = \frac{{{N}}}{{1 + ({A_val:.6g})\,e^{{-{k*N:.6g}\, t}}}}")

P_eval = logistic_analytic(t_eval, k, N, P0)
st.markdown("**Evaluación**")
st.latex(fr"P({t_eval}) = \frac{{{N}}}{{1 + ({A_val:.6g})\,e^{{-{k*N:.6g}\cdot{t_eval}}}}} = {P_eval:.6f}")

# ---------- Section: Simulation ----------
st.header("2) Simulación (RK4 vs. Sol. analítica)")
t, Pn, rk4_table = simulate_numeric(k, N, P0, tmax, dt, steps_to_log=10)
Pa = np.array([logistic_analytic(tt, k, N, P0) for tt in t])

df = pd.DataFrame({"t": t, "P_numérico": Pn, "P_analítico": Pa})
st.line_chart(df.set_index("t"))

col1, col2 = st.columns(2)
with col1:
    st.subheader("Primeros pasos de RK4 (detallados)")
    st.dataframe(rk4_table.round(6))
with col2:
    st.subheader("Descargas")
    csv_buf = io.StringIO()
    df.to_csv(csv_buf, index=False)
    st.download_button("Descargar resultados (CSV)", data=csv_buf.getvalue(), file_name="resultados_verhulst.csv", mime="text/csv")
    st.download_button("Descargar tabla RK4 (CSV)", data=rk4_table.to_csv(index=False), file_name="rk4_pasos.csv", mime="text/csv")
st.info(f"P({tmax}) ≈ numérico = {Pn[-1]:.6f}, analítico = {Pa[-1]:.6f}")

# ---------- Section: 2D Agent-based infection map ----------
st.header("3) Simulación tipo mapa de contagio (agentes)")
st.caption("Puntos blancos = susceptibles, rojos = infectados, verdes = recuperados (si se activa recuperación).")

# Parameters for agent sim
with st.expander("Parámetros de la simulación de agentes"):
    n_agents = st.number_input("Cantidad de agentes", min_value=50, max_value=5000, value=400, step=50)
    init_infected = st.number_input("Infectados iniciales", min_value=1, max_value=1000, value=10, step=1)
    radius = st.slider("Radio de contagio", min_value=0.005, max_value=0.2, value=0.03, step=0.005)
    beta = st.slider("Probabilidad de contagio por contacto (β)", min_value=0.0, max_value=1.0, value=0.25, step=0.05)
    speed = st.slider("Velocidad de movimiento (px/tick)", min_value=0.0, max_value=3.0, value=1.0, step=0.1)
    steps = st.number_input("Cantidad de pasos a simular", min_value=10, max_value=2000, value=500, step=10)
    delay_ms = st.slider("Retardo entre frames (ms)", min_value=0, max_value=200, value=20, step=5)
    use_recovery = st.checkbox("Activar recuperación", value=True)
    recov_time = st.number_input("Tiempo para recuperarse (pasos)", min_value=1, max_value=5000, value=300) if use_recovery else None

# Session state setup
if "agents_state" not in st.session_state:
    st.session_state.agents_state = None

def init_agents(n, init_I):
    # positions in [0,1]^2
    pos = np.random.rand(n, 2)
    # velocities random directions
    angles = np.random.rand(n) * 2*np.pi
    vel = np.c_[np.cos(angles), np.sin(angles)]
    # states: 0=S, 1=I, 2=R
    state = np.zeros(n, dtype=int)
    state[:init_I] = 1
    np.random.shuffle(state)
    # infection timers
    timer = np.zeros(n, dtype=int)
    return pos, vel, state, timer

def step_agents(pos, vel, state, timer, radius, beta, speed, use_recovery=False, recov_time=None):
    n = len(state)
    # move
    pos += vel * (speed/100.0)  # scale to keep in [0,1] nicely
    # bounce on borders
    for d in range(2):
        over = pos[:, d] > 1
        under = pos[:, d] < 0
        vel[over | under, d] *= -1
        pos[over, d] = 1 - (pos[over, d] - 1)
        pos[under, d] = -pos[under, d]

    # infection
    infected_idx = np.where(state == 1)[0]
    susceptible_idx = np.where(state == 0)[0]
    if len(infected_idx) and len(susceptible_idx):
        # compute pairwise distances (vectorized with broadcasting)
        inf_pos = pos[infected_idx][:, None, :]
        sus_pos = pos[susceptible_idx][None, :, :]
        d2 = np.sum((inf_pos - sus_pos)**2, axis=2)
        contact = d2 <= radius**2
        if np.any(contact):
            # for each susceptible with any infected neighbor, infect with prob beta
            exposed = susceptible_idx[np.any(contact, axis=0)]
            rng = np.random.rand(len(exposed))
            newly = exposed[rng < beta]
            state[newly] = 1  # become infected

    # recovery
    if use_recovery and recov_time and recov_time > 0:
        timer[state == 1] += 1
        recovered = np.where((state == 1) & (timer >= recov_time))[0]
        state[recovered] = 2

    return pos, vel, state, timer

# Controls
colA, colB = st.columns([1,1])
with colA:
    if st.button("🔄 Reiniciar agentes"):
        st.session_state.agents_state = init_agents(int(n_agents), int(init_infected))
with colB:
    start = st.button("▶️ Iniciar simulación")

# Initialize if needed
if st.session_state.agents_state is None:
    st.session_state.agents_state = init_agents(int(n_agents), int(init_infected))

pos, vel, state, timer = st.session_state.agents_state

# Placeholder for animation
ph = st.empty()
metrics = st.empty()

if start:
    # Run loop
    for i in range(int(steps)):
        pos, vel, state, timer = step_agents(pos, vel, state, timer, radius, beta, speed, use_recovery, recov_time)
        st.session_state.agents_state = (pos, vel, state, timer)

        # draw scatter via matplotlib
        fig, ax = plt.subplots(figsize=(6,6))
        ax.set_xlim(0,1); ax.set_ylim(0,1); ax.set_xticks([]); ax.set_yticks([])
        ax.scatter(pos[state==0,0], pos[state==0,1], s=8, label="S", alpha=0.8)
        ax.scatter(pos[state==1,0], pos[state==1,1], s=8, label="I", alpha=0.8)
        ax.scatter(pos[state==2,0], pos[state==2,1], s=8, label="R", alpha=0.8)
        # default matplotlib colors: C0 (blue) for S, C1 (orange) for I, C2 (green) for R
        ax.legend(loc="upper right")
        fig.tight_layout()
        ph.pyplot(fig)
        plt.close(fig)

        S = int(np.sum(state==0)); I = int(np.sum(state==1)); R = int(np.sum(state==2))
        metrics.markdown(f"**Paso {i+1}/{int(steps)}** — S: {S}  |  I: {I}  |  R: {R}")
        time.sleep(max(0, int(delay_ms)/1000.0))

st.caption("Sugerencia: si querés colores específicos (blanco = S, rojo = I, verde = R), decime y lo ajusto.")
