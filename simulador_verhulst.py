"""
Simulador de Modelo de Verhulst para Propagación de Infecciones
================================================================
Modelo logístico aplicado a epidemiología y crecimiento poblacional limitado.

Ecuación: dP/dt = k·P·(N - P)

Donde:
- P(t) = población infectada en el tiempo t
- N = población límite (capacidad máxima)
- k = constante de propagación
- t = tiempo (días)

Características:
- Entrada de datos observados (día, infectados)
- Ajuste automático de parámetros k y N
- Predicción futura
- Visualización completa con pasos del análisis
- Gráficos comparativos datos reales vs modelo
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from scipy.integrate import odeint
from scipy.optimize import curve_fit
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


class VerhulstSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Verhulst - Propagación de Infecciones")
        self.root.geometry("1400x900")
        
        # Theme color (matching launcher - usando verde para epidemiología)
        self.theme_color = "#27ae60"  # Green for Verhulst/Epidemiology
        self.theme_color_light = "#2ecc71"
        self.theme_color_dark = "#1e8449"
        
        # Model parameters
        self.k_value = tk.DoubleVar(value=0.001)  # Constante de propagación
        self.N_value = tk.DoubleVar(value=1000.0)  # Población límite
        self.P0_value = tk.DoubleVar(value=10.0)  # Población inicial infectada
        self.t_max = tk.DoubleVar(value=100.0)  # Días máximos de simulación
        
        # Auto-fit parameters
        self.auto_fit = tk.BooleanVar(value=True)
        self.solve_from_two_points = tk.BooleanVar(value=False)
        
        # Data points storage
        self.data_points = []  # List of tuples (day, infected)
        
        # Display options
        self.show_solution_steps = tk.BooleanVar(value=True)
        self.show_derivative = tk.BooleanVar(value=True)
        
        # Agent simulation parameters
        self.agent_n = tk.IntVar(value=400)
        self.agent_init_infected = tk.IntVar(value=10)
        self.agent_radius = tk.DoubleVar(value=0.03)
        self.agent_beta = tk.DoubleVar(value=0.25)
        self.agent_speed = tk.DoubleVar(value=1.0)
        self.agent_steps = tk.IntVar(value=500)
        self.agent_use_recovery = tk.BooleanVar(value=True)
        self.agent_recovery_time = tk.IntVar(value=300)
        self.agents_state = None  # (pos, vel, state, timer)
        
        # Create UI
        self._create_ui()
        
    def _create_ui(self):
        """Create the main user interface."""
        # Configure theme styles
        style = ttk.Style()
        style.configure('Themed.TButton', 
                       background=self.theme_color,
                       foreground='white',
                       borderwidth=1,
                       focuscolor='none',
                       padding=6)
        style.map('Themed.TButton',
                 background=[('active', self.theme_color_light)],
                 foreground=[('active', 'white')])
        
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (controls)
        self.left_panel = ttk.Frame(main_container, width=400)
        main_container.add(self.left_panel, weight=0)
        
        # Right panel (plots and results)
        self.right_panel = ttk.Frame(main_container)
        main_container.add(self.right_panel, weight=1)
        
        # Create sections
        self._create_model_info()
        self._create_data_input()
        self._create_parameters_input()
        self._create_simulation_controls()
        self._create_control_buttons()
        self._create_data_display()
        
    def _create_model_info(self):
        """Create model information display."""
        info_frame = ttk.LabelFrame(self.left_panel, text="Modelo de Verhulst")
        info_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)
        
        info_text = (
            "Ecuación Diferencial:\n"
            "dP/dt = k·P·(N - P)\n\n"
            "Solución Analítica:\n"
            "P(t) = N / (1 + ((N-P₀)/P₀)·e^(-k·N·t))\n\n"
            "Parámetros:\n"
            "• k: tasa de propagación\n"
            "• N: población límite\n"
            "• P₀: población inicial infectada"
        )
        
        label = tk.Label(info_frame, text=info_text, 
                        font=("Courier", 9), justify=tk.LEFT,
                        bg='#f0f0f0', padx=10, pady=10)
        label.pack(fill=tk.X, padx=5, pady=5)
        
    def _create_data_input(self):
        """Create data point input section."""
        data_frame = ttk.LabelFrame(self.left_panel, text="Datos Observados")
        data_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        
        ttk.Label(data_frame, text="Ingresa pares (día, infectados):",
                 font=("Arial", 9, "bold")).pack(anchor="w", padx=5, pady=(5, 2))
        
        # Single point input
        input_row = ttk.Frame(data_frame)
        input_row.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(input_row, text="Día:", width=8).pack(side=tk.LEFT, padx=2)
        self.day_entry = ttk.Entry(input_row, width=8)
        self.day_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(input_row, text="Infectados:", width=10).pack(side=tk.LEFT, padx=2)
        self.infected_entry = ttk.Entry(input_row, width=8)
        self.infected_entry.pack(side=tk.LEFT, padx=2)
        
        tk.Button(input_row, text="Agregar", 
                  command=self._add_data_point,
                  bg=self.theme_color, fg='white',
                  activebackground=self.theme_color_light,
                  activeforeground='white',
                  relief=tk.RAISED, bd=2,
                  font=("Arial", 9, "bold"),
                  cursor='hand2',
                  width=8).pack(side=tk.LEFT, padx=2)
        
        # Quick examples
        examples_frame = ttk.Frame(data_frame)
        examples_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(examples_frame, text="Ejemplos rápidos:",
                 font=("Arial", 8, "italic")).pack(anchor="w")
        
        btn_frame = ttk.Frame(data_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Button(btn_frame, text="COVID-19", 
                  command=lambda: self._load_example_data("covid"),
                  bg=self.theme_color, fg='white',
                  activebackground=self.theme_color_light,
                  activeforeground='white',
                  relief=tk.RAISED, bd=2,
                  font=("Arial", 9, "bold"),
                  cursor='hand2',
                  width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Gripe", 
                  command=lambda: self._load_example_data("flu"),
                  bg=self.theme_color, fg='white',
                  activebackground=self.theme_color_light,
                  activeforeground='white',
                  relief=tk.RAISED, bd=2,
                  font=("Arial", 9, "bold"),
                  cursor='hand2',
                  width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Limpiar", 
                  command=self._clear_data,
                  bg=self.theme_color, fg='white',
                  activebackground=self.theme_color_light,
                  activeforeground='white',
                  relief=tk.RAISED, bd=2,
                  font=("Arial", 9, "bold"),
                  cursor='hand2',
                  width=12).pack(side=tk.LEFT, padx=2)
        
    def _create_parameters_input(self):
        """Create parameter input controls."""
        param_frame = ttk.LabelFrame(self.left_panel, text="Parámetros del Modelo")
        param_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        
        # Auto-fit checkbox
        ttk.Checkbutton(param_frame, text="Ajustar k y N automáticamente desde datos", 
                       variable=self.auto_fit,
                       command=self._toggle_auto_fit).pack(anchor="w", padx=5, pady=5)
        
        # Solve from 2 points checkbox
        ttk.Checkbutton(param_frame, text="Resolver k desde 2 puntos (requiere N y P₀)", 
                       variable=self.solve_from_two_points,
                       command=self._toggle_solve_mode).pack(anchor="w", padx=5, pady=5)
        
        # k parameter
        k_frame = ttk.Frame(param_frame)
        k_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(k_frame, text="k (propagación):", width=18).pack(side=tk.LEFT)
        self.k_entry = ttk.Entry(k_frame, textvariable=self.k_value, width=12)
        self.k_entry.pack(side=tk.LEFT, padx=2)
        
        # N parameter
        n_frame = ttk.Frame(param_frame)
        n_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(n_frame, text="N (población límite):", width=18).pack(side=tk.LEFT)
        self.n_entry = ttk.Entry(n_frame, textvariable=self.N_value, width=12)
        self.n_entry.pack(side=tk.LEFT, padx=2)
        
        # P0 parameter
        p0_frame = ttk.Frame(param_frame)
        p0_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(p0_frame, text="P₀ (inicial):", width=18).pack(side=tk.LEFT)
        self.p0_entry = ttk.Entry(p0_frame, textvariable=self.P0_value, width=12)
        self.p0_entry.pack(side=tk.LEFT, padx=2)
        
    def _create_simulation_controls(self):
        """Create simulation control parameters."""
        sim_frame = ttk.LabelFrame(self.left_panel, text="Control de Simulación")
        sim_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        
        # Max time
        t_frame = ttk.Frame(sim_frame)
        t_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(t_frame, text="Días máximos:", width=18).pack(side=tk.LEFT)
        ttk.Entry(t_frame, textvariable=self.t_max, width=12).pack(side=tk.LEFT, padx=2)
        
        # Display options
        ttk.Checkbutton(sim_frame, text="Mostrar pasos de solución", 
                       variable=self.show_solution_steps).pack(anchor="w", padx=5, pady=2)
        ttk.Checkbutton(sim_frame, text="Mostrar gráfico de derivada", 
                       variable=self.show_derivative).pack(anchor="w", padx=5, pady=2)
        
    def _create_control_buttons(self):
        """Create main action buttons."""
        button_frame = ttk.LabelFrame(self.left_panel, text="Acciones")
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        
        tk.Button(button_frame, text="🧮 Simular Propagación", 
                  command=self.simulate,
                  bg=self.theme_color, fg='white',
                  activebackground=self.theme_color_light,
                  activeforeground='white',
                  relief=tk.RAISED, bd=2,
                  font=("Arial", 10, "bold"),
                  cursor='hand2').pack(fill=tk.X, padx=8, pady=4)
        tk.Button(button_frame, text="🧹 Limpiar Todo", 
                  command=self.clear_all,
                  bg=self.theme_color, fg='white',
                  activebackground=self.theme_color_light,
                  activeforeground='white',
                  relief=tk.RAISED, bd=2,
                  font=("Arial", 10, "bold"),
                  cursor='hand2').pack(fill=tk.X, padx=8, pady=4)
        
        # Advanced features
        tk.Button(button_frame, text="🎬 Simulación de Agentes", 
                  command=self.show_agent_simulation,
                  bg=self.theme_color_dark, fg='white',
                  activebackground=self.theme_color,
                  activeforeground='white',
                  relief=tk.RAISED, bd=2,
                  font=("Arial", 10, "bold"),
                  cursor='hand2').pack(fill=tk.X, padx=8, pady=4)
        
        tk.Button(button_frame, text="📊 Tabla RK4 Detallada", 
                  command=self.show_rk4_table,
                  bg=self.theme_color_dark, fg='white',
                  activebackground=self.theme_color,
                  activeforeground='white',
                  relief=tk.RAISED, bd=2,
                  font=("Arial", 10, "bold"),
                  cursor='hand2').pack(fill=tk.X, padx=8, pady=4)
        
        tk.Button(button_frame, text="💾 Exportar a CSV", 
                  command=self.export_to_csv,
                  bg=self.theme_color_dark, fg='white',
                  activebackground=self.theme_color,
                  activeforeground='white',
                  relief=tk.RAISED, bd=2,
                  font=("Arial", 10, "bold"),
                  cursor='hand2').pack(fill=tk.X, padx=8, pady=4)
        
    def _create_data_display(self):
        """Create data points display."""
        display_frame = ttk.LabelFrame(self.left_panel, text="Datos Ingresados")
        display_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)
        
        # Scrolled text for data points
        self.txt_data = ScrolledText(display_frame, wrap='word', 
                                     font=("Consolas", 9), height=8)
        self.txt_data.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        self._update_data_display()
        
    def _toggle_auto_fit(self):
        """Enable/disable manual parameter input based on auto-fit."""
        if self.auto_fit.get():
            self.solve_from_two_points.set(False)
        self._update_entry_states()
        
    def _toggle_solve_mode(self):
        """Enable/disable based on solve from 2 points mode."""
        if self.solve_from_two_points.get():
            self.auto_fit.set(False)
        self._update_entry_states()
    
    def _update_entry_states(self):
        """Update entry field states based on current mode."""
        if self.auto_fit.get():
            # Auto-fit mode: disable k and N
            self.k_entry.config(state='disabled')
            self.n_entry.config(state='disabled')
            self.p0_entry.config(state='disabled')
        elif self.solve_from_two_points.get():
            # 2-point solve mode: disable k, enable N and P0
            self.k_entry.config(state='disabled')
            self.n_entry.config(state='normal')
            self.p0_entry.config(state='normal')
        else:
            # Manual mode: enable all
            self.k_entry.config(state='normal')
            self.n_entry.config(state='normal')
            self.p0_entry.config(state='normal')
        
    def _add_data_point(self):
        """Add a data point to the list."""
        try:
            day = float(self.day_entry.get())
            infected = float(self.infected_entry.get())
            
            if day < 0 or infected < 0:
                messagebox.showerror("Error", "Los valores deben ser positivos")
                return
            
            self.data_points.append((day, infected))
            self.data_points.sort(key=lambda x: x[0])  # Sort by day
            
            # Clear entries
            self.day_entry.delete(0, tk.END)
            self.infected_entry.delete(0, tk.END)
            
            # Update display
            self._update_data_display()
            
        except ValueError:
            messagebox.showerror("Error", "Ingresa valores numéricos válidos")
            
    def _load_example_data(self, example_type):
        """Load example data sets."""
        self.data_points.clear()
        
        if example_type == "covid":
            # Ejemplo COVID-19 (primeros 30 días)
            self.data_points = [
                (0, 10), (5, 45), (10, 180), (15, 450), 
                (20, 850), (25, 1200), (30, 1450)
            ]
            self.N_value.set(2000)
            self.t_max.set(60)
            
        elif example_type == "flu":
            # Ejemplo Gripe estacional
            self.data_points = [
                (0, 5), (3, 25), (7, 95), (10, 200), 
                (14, 350), (21, 480), (28, 490)
            ]
            self.N_value.set(500)
            self.t_max.set(50)
            
        self._update_data_display()
        
    def _clear_data(self):
        """Clear all data points."""
        self.data_points.clear()
        self._update_data_display()
        
    def _update_data_display(self):
        """Update the data points display."""
        self.txt_data.delete(1.0, tk.END)
        
        if not self.data_points:
            self.txt_data.insert(tk.END, "No hay datos ingresados.\n\n")
            self.txt_data.insert(tk.END, "Agrega puntos manualmente o\n")
            self.txt_data.insert(tk.END, "usa los ejemplos rápidos.")
        else:
            self.txt_data.insert(tk.END, "Día\tInfectados\n")
            self.txt_data.insert(tk.END, "─" * 25 + "\n")
            for day, infected in self.data_points:
                self.txt_data.insert(tk.END, f"{day:.0f}\t{infected:.0f}\n")
            self.txt_data.insert(tk.END, f"\nTotal: {len(self.data_points)} puntos")
            
    def simulate(self):
        """Run the Verhulst simulation."""
        try:
            # Clear right panel
            for widget in self.right_panel.winfo_children():
                widget.destroy()
            
            # Get parameters
            P0 = self.P0_value.get()
            t_max = self.t_max.get()
            
            # Determine which mode we're in
            if self.solve_from_two_points.get():
                # Solve k from 2 points
                if len(self.data_points) < 2:
                    messagebox.showerror("Error", 
                        "Se necesitan exactamente 2 puntos para resolver k.\n" +
                        "Agrega 2 puntos de datos (día, infectados).")
                    return
                
                N = self.N_value.get()
                # Use P0 from user input (should match t=0 behavior)
                P0_input = self.P0_value.get()
                
                # Check if first point is at t=0, if so use that as P0
                if abs(self.data_points[0][0]) < 0.01:
                    P0 = self.data_points[0][1]
                    self.P0_value.set(P0)
                else:
                    P0 = P0_input
                
                k = self._solve_k_from_two_points(P0, N)
                if k is None:
                    return
                self.k_value.set(k)
                
            elif self.data_points and self.auto_fit.get():
                # Auto-fit from multiple points
                k, N, P0 = self._fit_parameters()
                self.k_value.set(k)
                self.N_value.set(N)
                self.P0_value.set(P0)
            else:
                # Manual mode
                k = self.k_value.get()
                N = self.N_value.get()
            
            # Create time array
            t = np.linspace(0, t_max, 1000)
            
            # Solve analytically
            P_analytical = self._verhulst_solution(t, P0, k, N)
            
            # Solve numerically (for verification)
            P_numerical = self._verhulst_numerical(t, P0, k, N)
            
            # Calculate derivative
            dPdt = k * P_analytical * (N - P_analytical)
            
            # Store data for export
            self.last_simulation_data = {
                'Tiempo_días': t,
                'P_Analítico': P_analytical,
                'P_Numérico': P_numerical,
                'dP/dt': dPdt,
                'k': [k] * len(t),
                'N': [N] * len(t),
                'P0': [P0] * len(t)
            }
            
            # Create plots
            self._create_plots(t, P_analytical, P_numerical, k, N, P0)
            
            # Show steps if requested
            if self.show_solution_steps.get():
                self._show_solution_steps(k, N, P0)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error en simulación:\n{str(e)}")
            import traceback
            traceback.print_exc()
            
    def _verhulst_solution(self, t, P0, k, N):
        """Analytical solution of Verhulst equation."""
        C = (N - P0) / P0
        return N / (1 + C * np.exp(-k * N * t))
    
    def _verhulst_numerical(self, t, P0, k, N):
        """Numerical solution of Verhulst equation."""
        def dPdt(P, t):
            return k * P * (N - P)
        
        P = odeint(dPdt, P0, t)
        return P.flatten()
    
    def _solve_k_from_two_points(self, P0, N):
        """
        Solve for k using exactly 2 data points.
        
        From the Verhulst solution: P(t) = N / (1 + C*e^(-k*N*t))
        where C = (N - P0) / P0
        
        Given two points (t1, P1) and (t2, P2):
        P1 = N / (1 + C*e^(-k*N*t1))
        P2 = N / (1 + C*e^(-k*N*t2))
        
        Solving for k:
        k = ln[(P1*(N-P2)) / (P2*(N-P1))] / (N*(t2-t1))
        """
        if len(self.data_points) < 2:
            messagebox.showerror("Error", "Se necesitan 2 puntos para resolver k")
            return None
        
        # Use first two points
        t1, P1 = self.data_points[0]
        t2, P2 = self.data_points[1]
        
        # Validate inputs
        if P1 <= 0 or P2 <= 0:
            messagebox.showerror("Error", "Las poblaciones deben ser positivas")
            return None
        
        if P1 >= N or P2 >= N:
            messagebox.showerror("Error", 
                f"Las poblaciones ({P1:.0f}, {P2:.0f}) deben ser menores que N ({N:.0f})")
            return None
        
        if abs(t2 - t1) < 1e-6:
            messagebox.showerror("Error", "Los tiempos deben ser diferentes")
            return None
        
        try:
            # Calculate k using the formula derived from Verhulst solution
            # From P(t) = N/(1 + C*e^(-k*N*t)), we get:
            # (N-P)/P = C*e^(-k*N*t)
            # For two points: [(N-P2)/P2] / [(N-P1)/P1] = e^(-k*N*(t2-t1))
            # k = -ln{[(N-P2)/P2] / [(N-P1)/P1]} / [N*(t2-t1)]
            # k = ln{[(N-P1)/P1] / [(N-P2)/P2]} / [N*(t2-t1)]
            # k = ln[P2*(N-P1) / (P1*(N-P2))] / [N*(t2-t1)]
            
            ratio1 = (N - P1) / P1  # At time t1
            ratio2 = (N - P2) / P2  # At time t2
            
            if ratio1 <= 0 or ratio2 <= 0:
                messagebox.showerror("Error", 
                    "Los datos no son consistentes con el modelo de Verhulst.\n" +
                    "Verifica que 0 < P1 < P2 < N")
                return None
            
            # k must be positive for growth (ratio1 > ratio2 when P2 > P1)
            k = np.log(ratio1 / ratio2) / (N * (t2 - t1))
            
            if k <= 0:
                messagebox.showerror("Error", 
                    f"k calculado es negativo ({k:.6f}).\n" +
                    "Los datos deben mostrar crecimiento (P2 > P1 y P1 < P2 < N)")
                return None
            
            # Show calculation details
            info_msg = (
                f"📊 Cálculo de k desde 2 puntos:\n\n"
                f"Punto 1: t₁ = {t1:.1f} días, P₁ = {P1:.0f}\n"
                f"Punto 2: t₂ = {t2:.1f} días, P₂ = {P2:.0f}\n"
                f"N (límite) = {N:.0f}\n"
                f"P₀ (inicial) = {P0:.0f}\n\n"
                f"Cálculo:\n"
                f"  ratio₁ = (N-P₁)/P₁ = {ratio1:.4f}\n"
                f"  ratio₂ = (N-P₂)/P₂ = {ratio2:.4f}\n\n"
                f"Fórmula: k = ln(ratio₁/ratio₂) / [N(t₂-t₁)]\n"
                f"       k = ln({ratio1:.4f}/{ratio2:.4f}) / [{N:.0f}×{t2-t1:.1f}]\n"
                f"       k = {np.log(ratio1/ratio2):.6f} / {N*(t2-t1):.2f}\n\n"
                f"✅ Resultado: k = {k:.6f}\n\n"
                f"Interpretación:\n"
                f"• La población crece de {P1:.0f} a {P2:.0f} en {t2-t1:.1f} días\n"
                f"• Con esta tasa, se alcanzará N/2 = {N/2:.0f} aproximadamente"
            )
            messagebox.showinfo("Cálculo de k", info_msg)
            
            return k
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al calcular k:\n{str(e)}")
            return None
    
    def _fit_parameters(self):
        """Fit k and N parameters from data points."""
        if len(self.data_points) < 3:
            messagebox.showwarning("Advertencia", 
                                  "Se necesitan al menos 3 puntos para ajustar parámetros")
            return self.k_value.get(), self.N_value.get(), self.P0_value.get()
        
        # Extract data
        days = np.array([d for d, _ in self.data_points])
        infected = np.array([i for _, i in self.data_points])
        
        # Use first point as P0
        P0 = infected[0]
        
        # Define fitting function
        def fit_func(t, k, N):
            return self._verhulst_solution(t, P0, k, N)
        
        # Initial guess
        N_guess = max(infected) * 2  # Estimate N as twice the max observed
        k_guess = 0.001
        
        try:
            # Fit
            popt, _ = curve_fit(fit_func, days, infected, 
                               p0=[k_guess, N_guess],
                               bounds=([1e-6, max(infected)], [1.0, 1e6]),
                               maxfev=10000)
            
            k_fit, N_fit = popt
            return k_fit, N_fit, P0
            
        except Exception as e:
            messagebox.showwarning("Ajuste", 
                                  f"No se pudo ajustar automáticamente.\nUsando valores manuales.")
            return self.k_value.get(), self.N_value.get(), P0
    
    def _create_plots(self, t, P_analytical, P_numerical, k, N, P0):
        """Create visualization plots."""
        # Determine number of subplots
        n_plots = 3 if self.show_derivative.get() else 2
        
        fig = Figure(figsize=(14, 4 * n_plots / 2))
        
        # Plot 1: Population over time
        ax1 = fig.add_subplot(n_plots, 1, 1)
        ax1.plot(t, P_analytical, 'b-', linewidth=2, label='Solución Analítica')
        ax1.plot(t, P_numerical, 'r--', linewidth=1, alpha=0.7, label='Solución Numérica')
        
        # Plot data points if available
        if self.data_points:
            days = [d for d, _ in self.data_points]
            infected = [i for _, i in self.data_points]
            ax1.plot(days, infected, 'go', markersize=8, label='Datos Observados',
                    markeredgecolor='darkgreen', markeredgewidth=1.5)
        
        ax1.axhline(y=N, color='gray', linestyle=':', linewidth=2, 
                   label=f'Límite N={N:.0f}')
        ax1.axhline(y=N/2, color='orange', linestyle=':', linewidth=1, 
                   label=f'Punto de inflexión (N/2={N/2:.0f})')
        
        ax1.set_xlabel('Tiempo (días)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Población Infectada', fontsize=11, fontweight='bold')
        ax1.set_title(f'Modelo de Verhulst: dP/dt = {k:.6f}·P·({N:.0f} - P)', 
                     fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='best', fontsize=9)
        
        # Plot 2: Phase plot (P vs dP/dt)
        ax2 = fig.add_subplot(n_plots, 1, 2)
        dPdt = k * P_analytical * (N - P_analytical)
        ax2.plot(P_analytical, dPdt, 'b-', linewidth=2)
        ax2.axvline(x=N/2, color='orange', linestyle='--', 
                   label=f'Máximo en P={N/2:.0f}')
        ax2.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
        
        ax2.set_xlabel('Población Infectada (P)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Tasa de Cambio (dP/dt)', fontsize=11, fontweight='bold')
        ax2.set_title('Diagrama de Fase: Tasa de Propagación vs Población', 
                     fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='best', fontsize=9)
        
        # Plot 3: Derivative over time (optional)
        if self.show_derivative.get():
            ax3 = fig.add_subplot(n_plots, 1, 3)
            dPdt = k * P_analytical * (N - P_analytical)
            ax3.plot(t, dPdt, 'g-', linewidth=2)
            
            # Mark maximum
            max_idx = np.argmax(dPdt)
            ax3.plot(t[max_idx], dPdt[max_idx], 'ro', markersize=10,
                    label=f'Máx en t={t[max_idx]:.1f} días')
            
            ax3.set_xlabel('Tiempo (días)', fontsize=11, fontweight='bold')
            ax3.set_ylabel('Tasa de Cambio (dP/dt)', fontsize=11, fontweight='bold')
            ax3.set_title('Velocidad de Propagación en el Tiempo', 
                         fontsize=12, fontweight='bold')
            ax3.grid(True, alpha=0.3)
            ax3.legend(loc='best', fontsize=9)
        
        fig.tight_layout()
        
        # Display in GUI
        canvas = FigureCanvasTkAgg(fig, self.right_panel)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def _show_solution_steps(self, k, N, P0):
        """Show detailed solution steps."""
        steps_window = tk.Toplevel(self.root)
        steps_window.title("Pasos de la Solución")
        steps_window.geometry("700x600")
        
        text = ScrolledText(steps_window, wrap='word', font=("Courier", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Build explanation
        C = (N - P0) / P0
        
        text.insert(tk.END, "═" * 70 + "\n")
        text.insert(tk.END, "SOLUCIÓN DETALLADA DEL MODELO DE VERHULST\n")
        text.insert(tk.END, "═" * 70 + "\n\n")
        
        # Show method used
        if self.solve_from_two_points.get() and len(self.data_points) >= 2:
            t1, P1 = self.data_points[0]
            t2, P2 = self.data_points[1]
            text.insert(tk.END, "🔍 MÉTODO: Resolución de k desde 2 puntos\n")
            text.insert(tk.END, "─" * 70 + "\n")
            text.insert(tk.END, f"Datos utilizados:\n")
            text.insert(tk.END, f"  Punto 1: t₁ = {t1:.1f}, P₁ = {P1:.0f}\n")
            text.insert(tk.END, f"  Punto 2: t₂ = {t2:.1f}, P₂ = {P2:.0f}\n\n")
            text.insert(tk.END, f"Fórmula de cálculo de k:\n")
            text.insert(tk.END, f"  k = ln[P₁(N-P₂)/(P₂(N-P₁))] / [N(t₂-t₁)]\n")
            text.insert(tk.END, f"  k = {k:.6f}\n\n")
        elif self.auto_fit.get():
            text.insert(tk.END, "🔍 MÉTODO: Ajuste automático desde múltiples datos\n")
            text.insert(tk.END, "─" * 70 + "\n")
            text.insert(tk.END, f"Puntos de datos usados: {len(self.data_points)}\n")
            text.insert(tk.END, f"Parámetros ajustados por mínimos cuadrados\n\n")
        else:
            text.insert(tk.END, "🔍 MÉTODO: Parámetros ingresados manualmente\n")
            text.insert(tk.END, "─" * 70 + "\n\n")
        
        text.insert(tk.END, "1. ECUACIÓN DIFERENCIAL\n")
        text.insert(tk.END, "─" * 70 + "\n")
        text.insert(tk.END, f"dP/dt = k·P·(N - P)\n\n")
        text.insert(tk.END, f"Donde:\n")
        text.insert(tk.END, f"  k = {k:.6f} (constante de propagación)\n")
        text.insert(tk.END, f"  N = {N:.2f} (población límite)\n")
        text.insert(tk.END, f"  P₀ = {P0:.2f} (población inicial)\n\n")
        
        text.insert(tk.END, "2. SEPARACIÓN DE VARIABLES\n")
        text.insert(tk.END, "─" * 70 + "\n")
        text.insert(tk.END, "dP / [P·(N - P)] = k·dt\n\n")
        
        text.insert(tk.END, "3. FRACCIONES PARCIALES\n")
        text.insert(tk.END, "─" * 70 + "\n")
        text.insert(tk.END, "1/[P·(N-P)] = (1/N)·[1/P + 1/(N-P)]\n\n")
        text.insert(tk.END, "(1/N)·∫[1/P + 1/(N-P)]dP = ∫k·dt\n\n")
        
        text.insert(tk.END, "4. INTEGRACIÓN\n")
        text.insert(tk.END, "─" * 70 + "\n")
        text.insert(tk.END, "(1/N)·[ln|P| - ln|N-P|] = k·t + C₁\n\n")
        text.insert(tk.END, "ln|P/(N-P)| = k·N·t + C₂\n\n")
        
        text.insert(tk.END, "5. APLICAR CONDICIÓN INICIAL P(0) = P₀\n")
        text.insert(tk.END, "─" * 70 + "\n")
        text.insert(tk.END, f"P/(N-P) = [P₀/(N-P₀)]·e^(k·N·t)\n\n")
        text.insert(tk.END, f"Calculando: C = (N-P₀)/P₀ = {C:.4f}\n\n")
        
        text.insert(tk.END, "6. SOLUCIÓN FINAL\n")
        text.insert(tk.END, "─" * 70 + "\n")
        text.insert(tk.END, f"P(t) = N / [1 + C·e^(-k·N·t)]\n\n")
        text.insert(tk.END, f"P(t) = {N:.2f} / [1 + {C:.4f}·e^(-{k*N:.6f}·t)]\n\n")
        
        text.insert(tk.END, "7. ANÁLISIS DEL COMPORTAMIENTO\n")
        text.insert(tk.END, "─" * 70 + "\n")
        text.insert(tk.END, f"• Límite cuando t→∞: P(∞) = N = {N:.2f}\n")
        text.insert(tk.END, f"• Punto de inflexión en: P = N/2 = {N/2:.2f}\n")
        
        # Calculate time to reach half capacity
        if P0 < N/2:
            t_half = np.log(C) / (k * N)
            text.insert(tk.END, f"• Tiempo al punto de inflexión: t ≈ {t_half:.2f} días\n")
        
        # Calculate time to 90% capacity
        t_90 = np.log(9 * C) / (k * N)
        text.insert(tk.END, f"• Tiempo al 90% de N: t ≈ {t_90:.2f} días\n\n")
        
        text.insert(tk.END, "8. INTERPRETACIÓN EPIDEMIOLÓGICA\n")
        text.insert(tk.END, "─" * 70 + "\n")
        text.insert(tk.END, "• Fase inicial: crecimiento exponencial (cuando P << N)\n")
        text.insert(tk.END, "• Fase de aceleración: hasta P = N/2\n")
        text.insert(tk.END, "• Fase de desaceleración: después de P = N/2\n")
        text.insert(tk.END, "• Fase de saturación: P → N cuando t → ∞\n\n")
        
        if self.data_points:
            text.insert(tk.END, "9. AJUSTE A DATOS OBSERVADOS\n")
            text.insert(tk.END, "─" * 70 + "\n")
            
            # Calculate R² if we have data
            days = np.array([d for d, _ in self.data_points])
            observed = np.array([i for _, i in self.data_points])
            predicted = self._verhulst_solution(days, P0, k, N)
            
            ss_res = np.sum((observed - predicted) ** 2)
            ss_tot = np.sum((observed - np.mean(observed)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            text.insert(tk.END, f"Coeficiente de determinación R² = {r_squared:.4f}\n")
            text.insert(tk.END, f"({'Excelente' if r_squared > 0.9 else 'Bueno' if r_squared > 0.7 else 'Moderado'} ajuste)\n\n")
        
        text.config(state='disabled')
    
    def show_rk4_table(self):
        """Show detailed RK4 integration steps."""
        try:
            # Get parameters
            k = self.k_value.get()
            N = self.N_value.get()
            P0 = self.P0_value.get()
            t_max = min(self.t_max.get(), 10)  # Only show first 10 days for clarity
            dt = 0.1
            
            # Create window
            rk4_window = tk.Toplevel(self.root)
            rk4_window.title("Tabla Detallada - Método RK4")
            rk4_window.geometry("900x600")
            
            # Create text widget
            text = ScrolledText(rk4_window, wrap='none', font=("Courier", 9))
            text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Header
            text.insert(tk.END, "═" * 100 + "\n")
            text.insert(tk.END, "MÉTODO RUNGE-KUTTA DE ORDEN 4 (RK4)\n")
            text.insert(tk.END, "═" * 100 + "\n\n")
            
            text.insert(tk.END, f"Ecuación: dP/dt = k·P·(N - P) = {k}·P·({N} - P)\n")
            text.insert(tk.END, f"Condición inicial: P(0) = {P0}\n")
            text.insert(tk.END, f"Paso de integración: dt = {dt}\n\n")
            
            text.insert(tk.END, "Fórmula RK4:\n")
            text.insert(tk.END, "  k₁ = f(tₙ, Pₙ)\n")
            text.insert(tk.END, "  k₂ = f(tₙ + dt/2, Pₙ + dt·k₁/2)\n")
            text.insert(tk.END, "  k₃ = f(tₙ + dt/2, Pₙ + dt·k₂/2)\n")
            text.insert(tk.END, "  k₄ = f(tₙ + dt, Pₙ + dt·k₃)\n")
            text.insert(tk.END, "  Pₙ₊₁ = Pₙ + (dt/6)·(k₁ + 2k₂ + 2k₃ + k₄)\n\n")
            
            text.insert(tk.END, "─" * 100 + "\n")
            text.insert(tk.END, f"{'n':>3} {'tₙ':>8} {'Pₙ':>12} {'k₁':>12} {'k₂':>12} {'k₃':>12} {'k₄':>12} {'Pₙ₊₁':>12}\n")
            text.insert(tk.END, "─" * 100 + "\n")
            
            # Calculate steps
            def f(t, P):
                return k * P * (N - P)
            
            t = 0.0
            P = P0
            steps = int(t_max / dt)
            
            for i in range(min(steps, 100)):  # Limit to 100 steps for display
                k1 = f(t, P)
                k2 = f(t + dt/2, P + dt*k1/2)
                k3 = f(t + dt/2, P + dt*k2/2)
                k4 = f(t + dt, P + dt*k3)
                P_next = P + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)
                
                text.insert(tk.END, 
                    f"{i:3d} {t:8.2f} {P:12.6f} {k1:12.6f} {k2:12.6f} {k3:12.6f} {k4:12.6f} {P_next:12.6f}\n")
                
                t += dt
                P = P_next
            
            text.insert(tk.END, "─" * 100 + "\n")
            text.insert(tk.END, f"\nValor final: P({t:.2f}) = {P:.6f}\n")
            
            # Compare with analytical
            P_analytical = self._verhulst_solution(np.array([t]), P0, k, N)[0]
            error = abs(P - P_analytical)
            rel_error = error / P_analytical * 100 if P_analytical > 0 else 0
            
            text.insert(tk.END, f"Solución analítica: P({t:.2f}) = {P_analytical:.6f}\n")
            text.insert(tk.END, f"Error absoluto: {error:.6e}\n")
            text.insert(tk.END, f"Error relativo: {rel_error:.4f}%\n")
            
            text.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar tabla RK4:\n{str(e)}")
    
    def export_to_csv(self):
        """Export simulation results to CSV."""
        try:
            # Check if we have simulation data
            if not hasattr(self, 'last_simulation_data'):
                messagebox.showwarning("Advertencia", 
                    "Primero ejecuta una simulación antes de exportar.")
                return
            
            # Ask for filename
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Guardar resultados como CSV"
            )
            
            if not filename:
                return
            
            # Create DataFrame
            df = pd.DataFrame(self.last_simulation_data)
            
            # Add data points if available
            if self.data_points:
                obs_df = pd.DataFrame(self.data_points, columns=['Día_Observado', 'Infectados_Observados'])
                # Merge on day (approximately)
                df = df.merge(obs_df, left_on='Tiempo_días', right_on='Día_Observado', how='left')
            
            # Save to CSV
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            messagebox.showinfo("Éxito", 
                f"Datos exportados exitosamente a:\n{filename}\n\n" +
                f"Registros: {len(df)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar CSV:\n{str(e)}")
    
    def show_agent_simulation(self):
        """Show agent-based infection simulation."""
        agent_window = tk.Toplevel(self.root)
        agent_window.title("Simulación de Agentes - Mapa de Contagio")
        agent_window.geometry("1200x800")
        
        # Left panel for controls
        control_frame = ttk.Frame(agent_window, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Right panel for visualization
        viz_frame = ttk.Frame(agent_window)
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Controls
        ttk.Label(control_frame, text="Parámetros de Simulación", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Number of agents
        ttk.Label(control_frame, text="Cantidad de agentes:").pack(anchor='w', padx=5)
        ttk.Entry(control_frame, textvariable=self.agent_n, width=15).pack(padx=5, pady=2)
        
        # Initial infected
        ttk.Label(control_frame, text="Infectados iniciales:").pack(anchor='w', padx=5)
        ttk.Entry(control_frame, textvariable=self.agent_init_infected, width=15).pack(padx=5, pady=2)
        
        # Infection radius
        ttk.Label(control_frame, text="Radio de contagio:").pack(anchor='w', padx=5)
        ttk.Scale(control_frame, from_=0.005, to=0.2, 
                 variable=self.agent_radius, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=2)
        
        # Infection probability
        ttk.Label(control_frame, text="Probabilidad de contagio (β):").pack(anchor='w', padx=5)
        ttk.Scale(control_frame, from_=0.0, to=1.0, 
                 variable=self.agent_beta, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=2)
        
        # Movement speed
        ttk.Label(control_frame, text="Velocidad de movimiento:").pack(anchor='w', padx=5)
        ttk.Scale(control_frame, from_=0.0, to=3.0, 
                 variable=self.agent_speed, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=2)
        
        # Simulation steps
        ttk.Label(control_frame, text="Pasos de simulación:").pack(anchor='w', padx=5)
        ttk.Entry(control_frame, textvariable=self.agent_steps, width=15).pack(padx=5, pady=2)
        
        # Recovery option
        ttk.Checkbutton(control_frame, text="Activar recuperación", 
                       variable=self.agent_use_recovery).pack(anchor='w', padx=5, pady=5)
        
        ttk.Label(control_frame, text="Tiempo para recuperarse:").pack(anchor='w', padx=5)
        ttk.Entry(control_frame, textvariable=self.agent_recovery_time, width=15).pack(padx=5, pady=2)
        
        # Status label
        status_label = ttk.Label(control_frame, text="", font=("Arial", 10))
        status_label.pack(pady=10)
        
        # Buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(pady=10)
        
        def init_agents():
            n = self.agent_n.get()
            init_I = self.agent_init_infected.get()
            
            # positions in [0,1]^2
            pos = np.random.rand(n, 2)
            # velocities random directions
            angles = np.random.rand(n) * 2 * np.pi
            vel = np.c_[np.cos(angles), np.sin(angles)]
            # states: 0=S, 1=I, 2=R
            state = np.zeros(n, dtype=int)
            state[:init_I] = 1
            np.random.shuffle(state)
            # infection timers
            timer = np.zeros(n, dtype=int)
            
            self.agents_state = (pos, vel, state, timer)
            status_label.config(text="Agentes inicializados")
            
            # Draw initial state
            draw_agents(pos, state)
        
        def step_agents():
            if self.agents_state is None:
                messagebox.showwarning("Advertencia", "Primero inicializa los agentes")
                return
            
            pos, vel, state, timer = self.agents_state
            radius = self.agent_radius.get()
            beta = self.agent_beta.get()
            speed = self.agent_speed.get()
            use_recovery = self.agent_use_recovery.get()
            recov_time = self.agent_recovery_time.get()
            
            n = len(state)
            # move
            pos += vel * (speed/100.0)
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
                inf_pos = pos[infected_idx][:, None, :]
                sus_pos = pos[susceptible_idx][None, :, :]
                d2 = np.sum((inf_pos - sus_pos)**2, axis=2)
                contact = d2 <= radius**2
                if np.any(contact):
                    exposed = susceptible_idx[np.any(contact, axis=0)]
                    rng = np.random.rand(len(exposed))
                    newly = exposed[rng < beta]
                    state[newly] = 1
            
            # recovery
            if use_recovery and recov_time > 0:
                timer[state == 1] += 1
                recovered = np.where((state == 1) & (timer >= recov_time))[0]
                state[recovered] = 2
            
            self.agents_state = (pos, vel, state, timer)
            return pos, state
        
        def draw_agents(pos, state):
            fig.clear()
            ax = fig.add_subplot(111)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_aspect('equal')
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Draw by state
            colors = ['lightblue', 'red', 'green']
            labels = ['Susceptible', 'Infectado', 'Recuperado']
            for s in range(3):
                mask = state == s
                if np.any(mask):
                    ax.scatter(pos[mask, 0], pos[mask, 1], 
                             c=colors[s], s=30, alpha=0.7, 
                             label=labels[s], edgecolors='black', linewidth=0.5)
            
            ax.legend(loc='upper right')
            ax.set_title("Mapa de Contagio - Simulación de Agentes", fontweight='bold')
            
            # Update counts
            S = int(np.sum(state == 0))
            I = int(np.sum(state == 1))
            R = int(np.sum(state == 2))
            status_label.config(text=f"S: {S}  |  I: {I}  |  R: {R}")
            
            canvas.draw()
        
        def run_simulation():
            if self.agents_state is None:
                messagebox.showwarning("Advertencia", "Primero inicializa los agentes")
                return
            
            steps = self.agent_steps.get()
            
            for i in range(steps):
                pos, state = step_agents()
                if i % 5 == 0:  # Update display every 5 steps
                    draw_agents(pos, state)
                    agent_window.update()
                
                # Stop if no more infected
                if np.sum(state == 1) == 0:
                    messagebox.showinfo("Simulación completa", 
                        f"La epidemia terminó en el paso {i+1}")
                    break
        
        tk.Button(btn_frame, text="🔄 Inicializar", 
                 command=init_agents,
                 bg=self.theme_color, fg='white',
                 font=("Arial", 10, "bold"),
                 cursor='hand2', width=15).pack(pady=5)
        
        tk.Button(btn_frame, text="▶️ Simular", 
                 command=run_simulation,
                 bg=self.theme_color_light, fg='white',
                 font=("Arial", 10, "bold"),
                 cursor='hand2', width=15).pack(pady=5)
        
        # Visualization setup
        fig = Figure(figsize=(8, 8))
        canvas = FigureCanvasTkAgg(fig, viz_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize with empty plot
        ax = fig.add_subplot(111)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title("Inicializa los agentes para comenzar", fontweight='bold')
        canvas.draw()
        
    def clear_all(self):
        """Clear all data and plots."""
        self._clear_data()
        for widget in self.right_panel.winfo_children():
            widget.destroy()


def main():
    root = tk.Tk()
    app = VerhulstSimulator(root)
    root.mainloop()


if __name__ == '__main__':
    main()
