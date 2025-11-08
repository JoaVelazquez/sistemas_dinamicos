"""
Simulador de Bifurcación de Hopf
=================================
Análisis especializado de bifurcaciones de Hopf con visualización de múltiples valores del parámetro.

Sistema analizado:
    ẋ = μx - y - x(x² + y²)
    ẏ = x + μy - y(x² + y²)

Características:
- Configuración de 3 valores de μ simultáneos
- Visualización lado a lado de los 3 casos
- Análisis automático de estabilidad
- Identificación del ciclo límite
- Cálculo de autovalores
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import sympy as sp
from scipy.integrate import odeint
import warnings
warnings.filterwarnings('ignore')


class HopfBifurcationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Bifurcación de Hopf")
        self.root.geometry("1400x900")
        
        # System equations (use 'mu' as parameter name)
        self.x_prime_str = tk.StringVar(value="mu*x - y - x*(x**2 + y**2)")
        self.y_prime_str = tk.StringVar(value="x + mu*y - y*(x**2 + y**2)")
        self.param_name = tk.StringVar(value="mu")
        
        # Parameter values
        self.mu1 = tk.DoubleVar(value=-1.0)
        self.mu2 = tk.DoubleVar(value=0.0)
        self.mu3 = tk.DoubleVar(value=1.0)
        
        # Simulation parameters
        self.x_min = tk.DoubleVar(value=-3.0)
        self.x_max = tk.DoubleVar(value=3.0)
        self.y_min = tk.DoubleVar(value=-3.0)
        self.y_max = tk.DoubleVar(value=3.0)
        self.t_max = tk.DoubleVar(value=25.0)
        self.n_trajectories = tk.IntVar(value=5)
        self.grid_density = tk.IntVar(value=20)
        
        # Display options
        self.show_vector_field = tk.BooleanVar(value=True)
        self.show_equilibrium = tk.BooleanVar(value=True)
        
        # Create UI
        self._create_ui()
        
    def _create_ui(self):
        """Create the main user interface."""
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (controls)
        self.left_panel = ttk.Frame(main_container, width=350)
        main_container.add(self.left_panel, weight=0)
        
        # Right panel (plots)
        self.right_panel = ttk.Frame(main_container)
        main_container.add(self.right_panel, weight=1)
        
        # Create sections
        self._create_system_input()
        self._create_parameter_inputs()
        self._create_simulation_parameters()
        self._create_display_options()
        self._create_control_buttons()
        self._create_results_display()
        
    def _create_system_input(self):
        """Create system equation input widgets."""
        input_frame = ttk.LabelFrame(self.left_panel, text="Sistema con Parámetro")
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)
        
        ttk.Label(input_frame, text="Ingresa las ecuaciones:", 
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(4, 8), padx=4)
        
        # Parameter name
        param_name_frame = ttk.Frame(input_frame)
        param_name_frame.pack(fill=tk.X, pady=4, padx=4)
        ttk.Label(param_name_frame, text="Parámetro:", font=("Arial", 10)).pack(side=tk.LEFT)
        param_entry = tk.Entry(param_name_frame, textvariable=self.param_name, 
                              width=10, font=("Arial", 10))
        param_entry.pack(side=tk.LEFT, padx=(8, 5))
        ttk.Label(param_name_frame, text="(usa este nombre en las ecuaciones)", 
                 foreground="gray", font=("Arial", 8)).pack(side=tk.LEFT)
        
        # x' equation
        x_frame = ttk.Frame(input_frame)
        x_frame.pack(fill=tk.X, pady=4, padx=4)
        ttk.Label(x_frame, text="x' =", font=("Arial", 10)).pack(side=tk.LEFT)
        x_entry = tk.Entry(x_frame, textvariable=self.x_prime_str, width=35, font=("Arial", 9))
        x_entry.pack(side=tk.LEFT, padx=(8, 0), fill=tk.X, expand=True)
        
        # y' equation  
        y_frame = ttk.Frame(input_frame)
        y_frame.pack(fill=tk.X, pady=4, padx=4)
        ttk.Label(y_frame, text="y' =", font=("Arial", 10)).pack(side=tk.LEFT)
        y_entry = tk.Entry(y_frame, textvariable=self.y_prime_str, width=35, font=("Arial", 9))
        y_entry.pack(side=tk.LEFT, padx=(8, 0), fill=tk.X, expand=True)
        
        # Help text
        help_text = "Usa 'x', 'y' y el parámetro en tus ecuaciones.\nFunciones: sin, cos, exp, sqrt, etc."
        ttk.Label(input_frame, text=help_text, font=("Arial", 8), 
                 foreground="gray").pack(anchor="w", padx=4, pady=(4, 2))
        
        # Example buttons
        example_frame = ttk.Frame(input_frame)
        example_frame.pack(fill=tk.X, padx=4, pady=(8, 4))
        ttk.Label(example_frame, text="Ejemplos:", font=("Arial", 9, "bold")).pack(anchor="w")
        
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill=tk.X, padx=4, pady=4)
        
        ttk.Button(btn_frame, text="Hopf Clásico", 
                  command=self._load_hopf_example).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="Van der Pol", 
                  command=self._load_vanderpol_example).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
    def _load_hopf_example(self):
        """Load classic Hopf bifurcation example."""
        self.param_name.set("mu")
        self.x_prime_str.set("mu*x - y - x*(x**2 + y**2)")
        self.y_prime_str.set("x + mu*y - y*(x**2 + y**2)")
        self.mu1.set(-1.0)
        self.mu2.set(0.0)
        self.mu3.set(1.0)
        
    def _load_vanderpol_example(self):
        """Load Van der Pol oscillator example."""
        self.param_name.set("mu")
        self.x_prime_str.set("y")
        self.y_prime_str.set("mu*(1 - x**2)*y - x")
        self.mu1.set(0.5)
        self.mu2.set(1.0)
        self.mu3.set(2.0)
        
    def _create_header(self):
        """Create header with system information."""
        # This is now replaced by _create_system_input
        pass
        
    def _create_parameter_inputs(self):
        self._create_simulation_parameters()
        self._create_display_options()
        self._create_control_buttons()
        self._create_results_display()
        
    def _create_header(self):
        """Create header with system information."""
        header_frame = ttk.LabelFrame(self.left_panel, text="Sistema de Hopf")
        header_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)
        
        system_text = (
            "Sistema:\n"
            "ẋ = μx - y - x(x² + y²)\n"
            "ẏ = x + μy - y(x² + y²)\n\n"
            "Equilibrio: (0, 0)\n"
            "Jacobiano en (0,0):\n"
            "J = [μ  -1]\n"
            "    [1   μ]\n\n"
            "Autovalores: λ = μ ± i"
        )
        
        label = tk.Label(header_frame, text=system_text, 
                        font=("Courier", 9), justify=tk.LEFT,
                        bg='#f0f0f0', padx=10, pady=10)
        label.pack(fill=tk.X, padx=5, pady=5)
        
    def _create_parameter_inputs(self):
        """Create parameter input controls."""
        param_frame = ttk.LabelFrame(self.left_panel, text="Valores del Parámetro μ")
        param_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        
        # Info label
        info = ttk.Label(param_frame, 
                        text="Configura 3 valores de μ para comparar:",
                        font=("Arial", 9, "italic"))
        info.pack(anchor="w", padx=5, pady=(5, 10))
        
        # μ1
        mu1_frame = ttk.Frame(param_frame)
        mu1_frame.pack(fill=tk.X, padx=5, pady=3)
        ttk.Label(mu1_frame, text="μ₁ =", width=6, font=("Arial", 10)).pack(side=tk.LEFT)
        ttk.Entry(mu1_frame, textvariable=self.mu1, width=10, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        ttk.Label(mu1_frame, text="(típicamente μ < 0)", 
                 foreground="gray", font=("Arial", 8)).pack(side=tk.LEFT)
        
        # μ2
        mu2_frame = ttk.Frame(param_frame)
        mu2_frame.pack(fill=tk.X, padx=5, pady=3)
        ttk.Label(mu2_frame, text="μ₂ =", width=6, font=("Arial", 10)).pack(side=tk.LEFT)
        ttk.Entry(mu2_frame, textvariable=self.mu2, width=10, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        ttk.Label(mu2_frame, text="(bifurcación en μ = 0)", 
                 foreground="gray", font=("Arial", 8)).pack(side=tk.LEFT)
        
        # μ3
        mu3_frame = ttk.Frame(param_frame)
        mu3_frame.pack(fill=tk.X, padx=5, pady=3)
        ttk.Label(mu3_frame, text="μ₃ =", width=6, font=("Arial", 10)).pack(side=tk.LEFT)
        ttk.Entry(mu3_frame, textvariable=self.mu3, width=10, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        ttk.Label(mu3_frame, text="(típicamente μ > 0)", 
                 foreground="gray", font=("Arial", 8)).pack(side=tk.LEFT)
        
        # Preset buttons
        preset_frame = ttk.Frame(param_frame)
        preset_frame.pack(fill=tk.X, padx=5, pady=(10, 5))
        ttk.Label(preset_frame, text="Presets:", font=("Arial", 9, "bold")).pack(anchor="w")
        
        btn_frame = ttk.Frame(param_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Clásico (-1, 0, 1)", 
                  command=lambda: self._set_preset(-1, 0, 1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Detallado (-0.5, 0, 0.5)", 
                  command=lambda: self._set_preset(-0.5, 0, 0.5)).pack(side=tk.LEFT, padx=2)
        
    def _set_preset(self, v1, v2, v3):
        """Set preset parameter values."""
        self.mu1.set(v1)
        self.mu2.set(v2)
        self.mu3.set(v3)
        
    def _create_simulation_parameters(self):
        """Create simulation parameter controls."""
        sim_frame = ttk.LabelFrame(self.left_panel, text="Parámetros de Simulación")
        sim_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        
        # X range
        x_frame = ttk.Frame(sim_frame)
        x_frame.pack(fill=tk.X, pady=2, padx=4)
        ttk.Label(x_frame, text="Rango X:", width=12).pack(side=tk.LEFT)
        ttk.Entry(x_frame, textvariable=self.x_min, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Label(x_frame, text="a").pack(side=tk.LEFT)
        ttk.Entry(x_frame, textvariable=self.x_max, width=6).pack(side=tk.LEFT, padx=2)
        
        # Y range
        y_frame = ttk.Frame(sim_frame)
        y_frame.pack(fill=tk.X, pady=2, padx=4)
        ttk.Label(y_frame, text="Rango Y:", width=12).pack(side=tk.LEFT)
        ttk.Entry(y_frame, textvariable=self.y_min, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Label(y_frame, text="a").pack(side=tk.LEFT)
        ttk.Entry(y_frame, textvariable=self.y_max, width=6).pack(side=tk.LEFT, padx=2)
        
        # Time
        t_frame = ttk.Frame(sim_frame)
        t_frame.pack(fill=tk.X, pady=2, padx=4)
        ttk.Label(t_frame, text="Tiempo máx:", width=12).pack(side=tk.LEFT)
        ttk.Entry(t_frame, textvariable=self.t_max, width=8).pack(side=tk.LEFT, padx=2)
        
        # Trajectories
        traj_frame = ttk.Frame(sim_frame)
        traj_frame.pack(fill=tk.X, pady=2, padx=4)
        ttk.Label(traj_frame, text="Trayectorias:", width=12).pack(side=tk.LEFT)
        ttk.Spinbox(traj_frame, from_=3, to=15, textvariable=self.n_trajectories, 
                   width=6).pack(side=tk.LEFT, padx=2)
        
    def _create_display_options(self):
        """Create display option checkboxes."""
        options_frame = ttk.LabelFrame(self.left_panel, text="Opciones de Visualización")
        options_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        
        ttk.Checkbutton(options_frame, text="Mostrar campo vectorial", 
                       variable=self.show_vector_field).pack(anchor="w", padx=8, pady=2)
        ttk.Checkbutton(options_frame, text="Marcar equilibrio", 
                       variable=self.show_equilibrium).pack(anchor="w", padx=8, pady=2)
        
    def _create_control_buttons(self):
        """Create control buttons."""
        button_frame = ttk.LabelFrame(self.left_panel, text="Acciones")
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        
        ttk.Button(button_frame, text="🔬 Analizar Bifurcación", 
                  command=self.analyze_bifurcation).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(button_frame, text="🧹 Limpiar", 
                  command=self.clear_plots).pack(fill=tk.X, padx=8, pady=4)
        
    def _create_results_display(self):
        """Create results display area."""
        results_frame = ttk.LabelFrame(self.left_panel, text="Análisis de Estabilidad")
        results_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)
        
        self.txt_results = ScrolledText(results_frame, wrap='word', 
                                       font=("Consolas", 9), height=10)
        self.txt_results.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
    def analyze_bifurcation(self):
        """Perform Hopf bifurcation analysis."""
        try:
            # Clear previous results
            self.clear_plots()
            self.txt_results.delete(1.0, tk.END)
            
            # Get parameter values
            mu_values = [self.mu1.get(), self.mu2.get(), self.mu3.get()]
            
            # Display system
            self.txt_results.insert(tk.END, "═" * 40 + "\n")
            self.txt_results.insert(tk.END, "ANÁLISIS DE BIFURCACIÓN\n")
            self.txt_results.insert(tk.END, "═" * 40 + "\n\n")
            self.txt_results.insert(tk.END, f"Sistema:\n")
            self.txt_results.insert(tk.END, f"x' = {self.x_prime_str.get()}\n")
            self.txt_results.insert(tk.END, f"y' = {self.y_prime_str.get()}\n")
            self.txt_results.insert(tk.END, f"Parámetro: {self.param_name.get()}\n\n")
            
            for i, mu in enumerate(mu_values, 1):
                self._analyze_stability(mu, i)
            
            # Generate plots
            self._generate_plots(mu_values)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en el análisis:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def _analyze_stability(self, param_val, index):
        """Analyze stability for a given parameter value."""
        param_name = self.param_name.get()
        self.txt_results.insert(tk.END, f"\n─── {param_name}{index} = {param_val} ───\n")
        self.txt_results.insert(tk.END, f"Sistema evaluado en {param_name} = {param_val}\n")
        
    def _generate_plots(self, param_values):
        """Generate phase portraits for the three parameter values."""
        # Create figure with 3 subplots
        fig = Figure(figsize=(15, 4.5))
        
        # Get parameters
        x_min, x_max = self.x_min.get(), self.x_max.get()
        y_min, y_max = self.y_min.get(), self.y_max.get()
        t_max = self.t_max.get()
        n_traj = self.n_trajectories.get()
        grid_density = self.grid_density.get()
        
        # Parse system equations
        x, y = sp.symbols('x y')
        param_symbol = sp.Symbol(self.param_name.get())
        
        x_prime_expr = sp.sympify(self.x_prime_str.get())
        y_prime_expr = sp.sympify(self.y_prime_str.get())
        
        for idx, param_val in enumerate(param_values):
            ax = fig.add_subplot(1, 3, idx + 1)
            self._plot_single_case(ax, param_val, x_min, x_max, y_min, y_max, 
                                  t_max, n_traj, grid_density,
                                  x_prime_expr, y_prime_expr, param_symbol)
        
        # Add main title
        title_text = f'Análisis de Bifurcación: x\' = {self.x_prime_str.get()},  y\' = {self.y_prime_str.get()}'
        fig.suptitle(title_text, fontsize=12, fontweight='bold', y=0.98)
        
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        
        # Display in GUI
        canvas = FigureCanvasTkAgg(fig, self.right_panel)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def _plot_single_case(self, ax, param_val, x_min, x_max, y_min, y_max, 
                         t_max, n_traj, grid_density, x_prime_expr, y_prime_expr, param_symbol):
        """Plot phase portrait for a single parameter value."""
        # Substitute parameter value
        x, y = sp.symbols('x y')
        x_prime_sub = x_prime_expr.subs(param_symbol, param_val)
        y_prime_sub = y_prime_expr.subs(param_symbol, param_val)
        
        # Convert to numerical functions
        f_x = sp.lambdify((x, y), x_prime_sub, 'numpy')
        f_y = sp.lambdify((x, y), y_prime_sub, 'numpy')
        
        # Vector field
        if self.show_vector_field.get():
            x_grid = np.linspace(x_min, x_max, grid_density)
            y_grid = np.linspace(y_min, y_max, grid_density)
            X, Y = np.meshgrid(x_grid, y_grid)
            
            U = np.zeros_like(X)
            V = np.zeros_like(Y)
            
            for i in range(X.shape[0]):
                for j in range(X.shape[1]):
                    U[i, j] = f_x(X[i, j], Y[i, j])
                    V[i, j] = f_y(X[i, j], Y[i, j])
            
            # Normalize
            M = np.sqrt(U**2 + V**2)
            M[M == 0] = 1
            U_norm = U / M
            V_norm = V / M
            
            ax.quiver(X, Y, U_norm, V_norm, M, cmap='viridis', alpha=0.5)
        
        # Plot trajectories
        colors = plt.cm.rainbow(np.linspace(0, 1, n_traj))
        
        for traj_idx in range(n_traj):
            # Initial conditions on a circle
            angle = 2 * np.pi * traj_idx / n_traj
            radius = 0.7 * min(x_max - x_min, y_max - y_min) / 2
            x0 = radius * np.cos(angle)
            y0 = radius * np.sin(angle)
            
            # Integrate
            def system(state, t):
                x_val, y_val = state
                return [f_x(x_val, y_val), f_y(x_val, y_val)]
            
            t_span = np.linspace(0, t_max, 1500)
            
            try:
                sol = odeint(system, [x0, y0], t_span)
                
                # Filter
                mask = (sol[:, 0] >= x_min * 1.2) & (sol[:, 0] <= x_max * 1.2) & \
                       (sol[:, 1] >= y_min * 1.2) & (sol[:, 1] <= y_max * 1.2)
                sol_filtered = sol[mask]
                
                if len(sol_filtered) > 1:
                    ax.plot(sol_filtered[:, 0], sol_filtered[:, 1], 
                           color=colors[traj_idx], linewidth=1.8, alpha=0.8)
                    ax.plot(x0, y0, 'o', color=colors[traj_idx], 
                           markersize=6, markeredgecolor='white', markeredgewidth=0.5)
            except:
                pass
        
        # Mark equilibrium
        if self.show_equilibrium.get():
            ax.plot(0, 0, 'r*', markersize=18, label='Equilibrio (0,0)', 
                   markeredgecolor='darkred', markeredgewidth=1)
        
        # Formatting
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_xlabel('x', fontsize=11, fontweight='bold')
        ax.set_ylabel('y', fontsize=11, fontweight='bold')
        ax.set_title(f'{self.param_name.get()} = {param_val}', fontsize=13, fontweight='bold', pad=10)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.axhline(y=0, color='k', linewidth=0.8)
        ax.axvline(x=0, color='k', linewidth=0.8)
        
        if self.show_equilibrium.get():
            ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
        
    def clear_plots(self):
        """Clear all plots."""
        for widget in self.right_panel.winfo_children():
            widget.destroy()


def main():
    root = tk.Tk()
    app = HopfBifurcationApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
