"""
Test script to demonstrate k calculation from 2 points in Verhulst model.

Given:
- N = 1000 (population limit)
- P0 = 10 (initial infected)
- Two observations: (t1, P1) and (t2, P2)

The CORRECT formula to calculate k is:
k = ln[(N-P1)/P1 / (N-P2)/P2] / [N(t2-t1)]
"""

import numpy as np

def calculate_k_from_two_points(t1, P1, t2, P2, N, P0):
    """
    Calculate k parameter from two data points.
    
    Parameters:
    - t1, P1: First observation (time, population)
    - t2, P2: Second observation (time, population)
    - N: Population limit
    - P0: Initial population
    
    Returns:
    - k: Propagation constant
    """
    # CORRECTED formula
    ratio1 = (N - P1) / P1
    ratio2 = (N - P2) / P2
    k = np.log(ratio1 / ratio2) / (N * (t2 - t1))
    
    return k

def verhulst_solution(t, P0, k, N):
    """Analytical solution of Verhulst equation."""
    C = (N - P0) / P0
    return N / (1 + C * np.exp(-k * N * t))

# Example 1: Simple case
print("=" * 70)
print("EJEMPLO 1: Propagación de virus en escuela")
print("=" * 70)
N = 1000  # Total students
P0 = 10   # Initially infected
t1, P1 = 5, 50    # Day 5: 50 infected
t2, P2 = 10, 150  # Day 10: 150 infected

k = calculate_k_from_two_points(t1, P1, t2, P2, N, P0)
print(f"\nDatos:")
print(f"  N (límite) = {N}")
print(f"  P₀ (inicial) = {P0}")
print(f"  Punto 1: t={t1}, P={P1}")
print(f"  Punto 2: t={t2}, P={P2}")
print(f"\nResultado: k = {k:.6f}")

# Verify: calculate P at t1 and t2 using the calculated k
P1_calc = verhulst_solution(t1, P0, k, N)
P2_calc = verhulst_solution(t2, P0, k, N)
print(f"\nVerificación:")
print(f"  P({t1}) calculado = {P1_calc:.2f} (esperado: {P1})")
print(f"  P({t2}) calculado = {P2_calc:.2f} (esperado: {P2})")

# Predict future
t_future = [15, 20, 30]
print(f"\nPredicciones:")
for t in t_future:
    P_pred = verhulst_solution(t, P0, k, N)
    print(f"  Día {t}: ~{P_pred:.0f} infectados")

# Example 2: COVID-like spread
print("\n" + "=" * 70)
print("EJEMPLO 2: Propagación tipo COVID-19")
print("=" * 70)
N = 5000
P0 = 5
t1, P1 = 10, 100
t2, P2 = 20, 800

k = calculate_k_from_two_points(t1, P1, t2, P2, N, P0)
print(f"\nDatos:")
print(f"  N (límite) = {N}")
print(f"  P₀ (inicial) = {P0}")
print(f"  Punto 1: t={t1}, P={P1}")
print(f"  Punto 2: t={t2}, P={P2}")
print(f"\nResultado: k = {k:.6f}")

P1_calc = verhulst_solution(t1, P0, k, N)
P2_calc = verhulst_solution(t2, P0, k, N)
print(f"\nVerificación:")
print(f"  P({t1}) calculado = {P1_calc:.2f} (esperado: {P1})")
print(f"  P({t2}) calculado = {P2_calc:.2f} (esperado: {P2})")

t_half = np.log((N - P0) / P0) / (k * N)
print(f"\nAnálisis:")
print(f"  Tiempo para llegar a N/2 = {N/2:.0f}: ~{t_half:.1f} días")
print(f"  Punto de máxima velocidad: P = {N/2:.0f}")

print("\n" + "=" * 70)
print("✓ Ahora puedes usar estos valores en el simulador!")
print("=" * 70)
