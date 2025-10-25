"""
Analizador de Sistemas Dinámicos No Lineales 2D
Basado en el analizador de sistemas lineales, adaptado para sistemas no lineales.

Características:
- Análisis de sistemas no lineales de la forma: x' = f(x, y), y' = g(x, y)
- Búsqueda automática de puntos de equilibrio
- Linearización en puntos de equilibrio
- Análisis de estabilidad (autovalores del Jacobiano)
- Retratos de fase con campos vectoriales
- Trayectorias interactivas (click para graficar)
- Nullclinas
- Separatrices (para puntos silla)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
# Increase the agg.path.chunksize to handle more complex plots
matplotlib.rcParams['agg.path.chunksize'] = 20000
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import sympy as sp
from scipy.integrate import odeint
from scipy.optimize import fsolve
import warnings
warnings.filterwarnings('ignore')


class NonlinearSystem2DApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Sistemas Dinámicos No Lineales 2D")
        self.root.geometry("1400x900")
        
        # System variables
        self.x_prime_str = tk.StringVar(value="y")  # x' = 
        self.y_prime_str = tk.StringVar(value="-sin(x)")  # y' = (péndulo simple)
        
        # Plot parameters
        self.x_min = tk.DoubleVar(value=-3.0)
        self.x_max = tk.DoubleVar(value=3.0)
        self.y_min = tk.DoubleVar(value=-3.0)
        self.y_max = tk.DoubleVar(value=3.0)
        self.t_max = tk.DoubleVar(value=20.0)
        self.grid_density = tk.IntVar(value=20)
        
        # Display options
        self.show_nullclines = tk.BooleanVar(value=True)
        self.show_equilibria = tk.BooleanVar(value=True)
        self.show_vector_field = tk.BooleanVar(value=True)
        self.show_separatrices = tk.BooleanVar(value=False)
        
        # Trajectory options
        self.num_trajectories = tk.IntVar(value=5)
        self.trajectory_direction = tk.StringVar(value="forward")  # "forward", "backward", "both"
        
        # Storage for analysis
        self.equilibrium_points = []
        self.clicked_trajectories = []
        self.current_system = None
        
        # Create UI
        self._create_ui()
        
        # Bind click event for interactive trajectories
        self.click_cid = None
        
    def _create_ui(self):
        """Create the main user interface."""
        # Main container with two panels
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (controls and results)
        self.left_panel = ttk.Frame(main_container, width=400)
        main_container.add(self.left_panel, weight=0)
        
        # Right panel (plots) with scrolling
        self.right_panel_container = ttk.Frame(main_container)
        main_container.add(self.right_panel_container, weight=1)
        
        # Create scrollable canvas for plots
        self.canvas = tk.Canvas(self.right_panel_container, bg='white')
        scrollbar_y = ttk.Scrollbar(self.right_panel_container, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar_x = ttk.Scrollbar(self.right_panel_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.right_panel = ttk.Frame(self.canvas)
        self.right_panel.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.right_panel, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Pack scrollbars and canvas
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Enable mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Populate left panel
        self._create_system_input()
        self._create_plot_parameters()
        self._create_display_options()
        self._create_control_buttons()
        self._create_results_display()
        
        # Create example systems
        self._create_example_systems()
        
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def _create_system_input(self):
        """Create system equation input widgets."""
        input_frame = ttk.LabelFrame(self.left_panel, text="Sistema No Lineal")
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)
        
        ttk.Label(input_frame, text="Ingresa las ecuaciones:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(4, 8), padx=4)
        
        # x' equation
        x_frame = ttk.Frame(input_frame)
        x_frame.pack(fill=tk.X, pady=4, padx=4)
        ttk.Label(x_frame, text="x' =", font=("Arial", 11)).pack(side=tk.LEFT)
        x_entry = tk.Entry(x_frame, textvariable=self.x_prime_str, width=30, font=("Arial", 10))
        x_entry.pack(side=tk.LEFT, padx=(8, 0), fill=tk.X, expand=True)
        
        # y' equation  
        y_frame = ttk.Frame(input_frame)
        y_frame.pack(fill=tk.X, pady=4, padx=4)
        ttk.Label(y_frame, text="y' =", font=("Arial", 11)).pack(side=tk.LEFT)
        y_entry = tk.Entry(y_frame, textvariable=self.y_prime_str, width=30, font=("Arial", 10))
        y_entry.pack(side=tk.LEFT, padx=(8, 0), fill=tk.X, expand=True)
        
        # Help text
        help_text = "Usa 'x' e 'y' para las variables.\nFunciones: sin, cos, exp, log, sqrt, etc."
        ttk.Label(input_frame, text=help_text, font=("Arial", 9), foreground="gray").pack(anchor="w", padx=4, pady=4)
        
    def _create_plot_parameters(self):
        """Create plot parameter controls."""
        param_frame = ttk.LabelFrame(self.left_panel, text="Parámetros de Graficación")
        param_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        
        # X range
        x_range_frame = ttk.Frame(param_frame)
        x_range_frame.pack(fill=tk.X, pady=2, padx=4)
        ttk.Label(x_range_frame, text="Rango X:", width=12).pack(side=tk.LEFT)
        ttk.Entry(x_range_frame, textvariable=self.x_min, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(x_range_frame, text="a").pack(side=tk.LEFT)
        ttk.Entry(x_range_frame, textvariable=self.x_max, width=8).pack(side=tk.LEFT, padx=2)
        
        # Y range
        y_range_frame = ttk.Frame(param_frame)
        y_range_frame.pack(fill=tk.X, pady=2, padx=4)
        ttk.Label(y_range_frame, text="Rango Y:", width=12).pack(side=tk.LEFT)
        ttk.Entry(y_range_frame, textvariable=self.y_min, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(y_range_frame, text="a").pack(side=tk.LEFT)
        ttk.Entry(y_range_frame, textvariable=self.y_max, width=8).pack(side=tk.LEFT, padx=2)
        
        # Time max
        t_frame = ttk.Frame(param_frame)
        t_frame.pack(fill=tk.X, pady=2, padx=4)
        ttk.Label(t_frame, text="Tiempo máx:", width=12).pack(side=tk.LEFT)
        ttk.Entry(t_frame, textvariable=self.t_max, width=8).pack(side=tk.LEFT, padx=2)
        
        # Grid density
        grid_frame = ttk.Frame(param_frame)
        grid_frame.pack(fill=tk.X, pady=2, padx=4)
        ttk.Label(grid_frame, text="Densidad grid:", width=12).pack(side=tk.LEFT)
        ttk.Scale(grid_frame, from_=10, to=40, variable=self.grid_density, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Label(grid_frame, textvariable=self.grid_density, width=4).pack(side=tk.LEFT)
        
    def _create_display_options(self):
        """Create display option checkboxes."""
        options_frame = ttk.LabelFrame(self.left_panel, text="Opciones de Visualización")
        options_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        
        ttk.Checkbutton(options_frame, text="Mostrar campo vectorial", variable=self.show_vector_field).pack(anchor="w", padx=4, pady=2)
        ttk.Checkbutton(options_frame, text="Mostrar nullclinas", variable=self.show_nullclines).pack(anchor="w", padx=4, pady=2)
        ttk.Checkbutton(options_frame, text="Mostrar puntos de equilibrio", variable=self.show_equilibria).pack(anchor="w", padx=4, pady=2)
        ttk.Checkbutton(options_frame, text="Mostrar separatrices (puntos silla)", variable=self.show_separatrices).pack(anchor="w", padx=4, pady=2)
        
        # Trajectory direction
        traj_frame = ttk.Frame(options_frame)
        traj_frame.pack(fill=tk.X, pady=4, padx=4)
        ttk.Label(traj_frame, text="Dirección de trayectorias:").pack(anchor="w")
        ttk.Radiobutton(traj_frame, text="Adelante", variable=self.trajectory_direction, value="forward").pack(anchor="w", padx=16)
        ttk.Radiobutton(traj_frame, text="Atrás", variable=self.trajectory_direction, value="backward").pack(anchor="w", padx=16)
        ttk.Radiobutton(traj_frame, text="Ambas", variable=self.trajectory_direction, value="both").pack(anchor="w", padx=16)
        
    def _create_control_buttons(self):
        """Create control buttons."""
        button_frame = ttk.LabelFrame(self.left_panel, text="Acciones")
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        
        ttk.Button(button_frame, text="Analizar Sistema", command=self.analyze_system).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(button_frame, text="Limpiar Gráficos", command=self.clear_plots).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(button_frame, text="Limpiar Trayectorias Click", 
                  command=self.clear_clicked_trajectories).pack(fill=tk.X, padx=8, pady=4)
        
    def _create_results_display(self):
        """Create results display area."""
        results_frame = ttk.LabelFrame(self.left_panel, text="Análisis del Sistema")
        results_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)
        
        self.txt_results = ScrolledText(results_frame, wrap='word', font=("Consolas", 9))
        self.txt_results.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
    def _create_example_systems(self):
        """Create example nonlinear systems."""
        examples_frame = ttk.LabelFrame(self.left_panel, text="Ejercicios")
        examples_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=8)
        
        # Create scrollable frame for exercises
        canvas_ex = tk.Canvas(examples_frame, height=200)
        scrollbar_ex = ttk.Scrollbar(examples_frame, orient="vertical", command=canvas_ex.yview)
        scrollable_frame = ttk.Frame(canvas_ex)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_ex.configure(scrollregion=canvas_ex.bbox("all"))
        )
        
        canvas_ex.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_ex.configure(yscrollcommand=scrollbar_ex.set)
        
        # All exercises from the image
        exercises = [
            ("Ej. 1", "y", "x*(3 - x)"),
            ("Ej. 2", "y", "x**3 - x"),
            ("Ej. 3", "y - x", "x**2 - 1"),
            ("Ej. 4", "x*y", "x**2 + y**2 - 1"),
            ("Ej. 5", "y - x*(x - x**2 - y**2)", "-x + y*(x - x**2 - y**2)"),
            ("Ej. 6", "-x + y - x*(x**2 + y**2)", "-x - y - y*(x**2 + y**2)"),
            ("Ej. 7", "x*(1 - x**2 - y**2) - y", "y*(1 - x**2 - y**2) + x"),
            ("Ej. 8", "x*(2 - x - y)", "y*(3 - 2*x - y)"),
            ("Ej. 11", "-x + x*y", "-2*x + x*y"),
            ("Ej. 12", "x**2 + y**2 - 2", "x**2 - y**2"),
            ("Ej. 13", "14*x - 0.5*x**2 - x*y", "16*y - 0.5*y**2 - x*y"),
            ("Ej. 14", "x*(3 - x) - 2*x*y", "y*(2 - y) - x*y"),
            ("Ej. 15", "x*(1 - x) - x*y", "x - y + x*y"),
            ("Ej. 16", "y", "-x + y*(1 - x**2)"),
            ("Ej. 17", "x + y**2", "-y"),
            ("Ej. 18", "y", "-sin(y)"),
        ]
        
        for i, (name, x_eq, y_eq) in enumerate(exercises):
            row = i // 3
            col = i % 3
            btn = ttk.Button(scrollable_frame, text=name,
                           command=lambda xe=x_eq, ye=y_eq, n=name: self._load_example(xe, ye, n))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
        
        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.columnconfigure(1, weight=1)
        scrollable_frame.columnconfigure(2, weight=1)
        
        canvas_ex.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_ex.pack(side=tk.RIGHT, fill=tk.Y)
        
    def _load_example(self, x_eq, y_eq, name=""):
        """Load an example system."""
        self.x_prime_str.set(x_eq)
        self.y_prime_str.set(y_eq)
        
        # Auto-adjust ranges based on exercise
        if "Ej. 13" in name or "Ej. 14" in name:
            # Larger ranges for competition/predator-prey models
            self.x_min.set(-1)
            self.x_max.set(20)
            self.y_min.set(-1)
            self.y_max.set(20)
        elif "Ej. 12" in name:
            # Larger range for x^2 + y^2 system
            self.x_min.set(-3)
            self.x_max.set(3)
            self.y_min.set(-3)
            self.y_max.set(3)
        else:
            # Default range
            self.x_min.set(-3)
            self.x_max.set(3)
            self.y_min.set(-3)
            self.y_max.set(3)
        
    def analyze_system(self):
        """Analyze the nonlinear system."""
        try:
            # Clear previous results
            self.txt_results.delete(1.0, tk.END)
            self.equilibrium_points = []
            
            # Parse equations
            x, y, t = sp.symbols('x y t')
            
            x_prime_expr = sp.sympify(self.x_prime_str.get())
            y_prime_expr = sp.sympify(self.y_prime_str.get())
            
            self.current_system = (x_prime_expr, y_prime_expr)
            
            # Display system
            self.txt_results.insert(tk.END, "═" * 50 + "\n")
            self.txt_results.insert(tk.END, "SISTEMA NO LINEAL\n")
            self.txt_results.insert(tk.END, "═" * 50 + "\n\n")
            self.txt_results.insert(tk.END, f"x' = {x_prime_expr}\n")
            self.txt_results.insert(tk.END, f"y' = {y_prime_expr}\n\n")
            
            # Find equilibrium points
            self._find_equilibrium_points(x_prime_expr, y_prime_expr)
            
            # Analyze each equilibrium point
            self._analyze_equilibrium_points(x_prime_expr, y_prime_expr)
            
            # Plot phase portrait
            self._plot_phase_portrait()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al analizar el sistema:\n{str(e)}")
            
    def _find_equilibrium_points(self, x_prime_expr, y_prime_expr):
        """Find equilibrium points numerically."""
        x, y = sp.symbols('x y')
        
        # Convert to numpy functions
        f_x = sp.lambdify((x, y), x_prime_expr, 'numpy')
        f_y = sp.lambdify((x, y), y_prime_expr, 'numpy')
        
        def system(vars):
            x_val, y_val = vars
            return [f_x(x_val, y_val), f_y(x_val, y_val)]
        
        # Search for equilibria in a grid
        x_range = np.linspace(self.x_min.get(), self.x_max.get(), 10)
        y_range = np.linspace(self.y_min.get(), self.y_max.get(), 10)
        
        equilibria_found = []
        tolerance = 1e-6
        
        for x0 in x_range:
            for y0 in y_range:
                try:
                    sol = fsolve(system, [x0, y0], full_output=True)
                    x_eq, y_eq = sol[0]
                    info = sol[1]
                    
                    # Check if solution is valid
                    if info['fvec'][0]**2 + info['fvec'][1]**2 < tolerance:
                        # Check if in range
                        if (self.x_min.get() <= x_eq <= self.x_max.get() and 
                            self.y_min.get() <= y_eq <= self.y_max.get()):
                            # Check if not already found
                            is_new = True
                            for ex, ey in equilibria_found:
                                if abs(x_eq - ex) < 0.1 and abs(y_eq - ey) < 0.1:
                                    is_new = False
                                    break
                            
                            if is_new:
                                equilibria_found.append((x_eq, y_eq))
                except:
                    pass
        
        self.equilibrium_points = equilibria_found
        
        self.txt_results.insert(tk.END, f"Puntos de equilibrio encontrados: {len(self.equilibrium_points)}\n")
        self.txt_results.insert(tk.END, "─" * 50 + "\n\n")
        
    def _analyze_equilibrium_points(self, x_prime_expr, y_prime_expr):
        """Analyze stability of equilibrium points using linearization."""
        x, y = sp.symbols('x y')
        
        # Compute Jacobian matrix
        J = sp.Matrix([
            [sp.diff(x_prime_expr, x), sp.diff(x_prime_expr, y)],
            [sp.diff(y_prime_expr, x), sp.diff(y_prime_expr, y)]
        ])
        
        for i, (x_eq, y_eq) in enumerate(self.equilibrium_points):
            self.txt_results.insert(tk.END, f"Punto de equilibrio #{i+1}: ({x_eq:.4f}, {y_eq:.4f})\n")
            self.txt_results.insert(tk.END, "─" * 50 + "\n")
            
            # Evaluate Jacobian at equilibrium
            J_eq = J.subs([(x, x_eq), (y, y_eq)])
            
            try:
                # Convert to float matrix
                J_numeric = np.array(J_eq.tolist(), dtype=float)
                
                self.txt_results.insert(tk.END, f"Jacobiano en ({x_eq:.4f}, {y_eq:.4f}):\n")
                self.txt_results.insert(tk.END, f"  [{J_numeric[0,0]:8.4f}  {J_numeric[0,1]:8.4f}]\n")
                self.txt_results.insert(tk.END, f"  [{J_numeric[1,0]:8.4f}  {J_numeric[1,1]:8.4f}]\n\n")
                
                # Show linearized system
                u_var, v_var = sp.symbols('u v')
                self.txt_results.insert(tk.END, "Sistema linearizado (u = x - x*, v = y - y*):\n")
                self.txt_results.insert(tk.END, f"  u' = {J_numeric[0,0]:.4f}*u + {J_numeric[0,1]:.4f}*v\n")
                self.txt_results.insert(tk.END, f"  v' = {J_numeric[1,0]:.4f}*u + {J_numeric[1,1]:.4f}*v\n\n")
                
                # Compute eigenvalues
                eigenvalues, eigenvectors = np.linalg.eig(J_numeric)
                
                # Compute trace and determinant
                trace = np.trace(J_numeric)
                det = np.linalg.det(J_numeric)
                
                self.txt_results.insert(tk.END, f"Traza: {trace:.4f}\n")
                self.txt_results.insert(tk.END, f"Determinante: {det:.4f}\n\n")
                
                self.txt_results.insert(tk.END, "Autovalores:\n")
                for j, eig in enumerate(eigenvalues):
                    if np.isreal(eig):
                        self.txt_results.insert(tk.END, f"  λ{j+1} = {eig.real:.4f}\n")
                    else:
                        self.txt_results.insert(tk.END, f"  λ{j+1} = {eig.real:.4f} + {eig.imag:.4f}i\n")
                
                # Check if hyperbolic (Hartman-Grobman applies)
                is_hyperbolic = self._is_hyperbolic(eigenvalues)
                
                self.txt_results.insert(tk.END, f"\nHiperbólico: {'SÍ' if is_hyperbolic else 'NO'}\n")
                
                if not is_hyperbolic:
                    self.txt_results.insert(tk.END, "⚠️  Punto crítico no hiperbólico - Se requiere análisis adicional\n")
                    self.txt_results.insert(tk.END, "   (Teorema de Hartman-Grobman NO aplica)\n")
                else:
                    self.txt_results.insert(tk.END, "✓  Teorema de Hartman-Grobman aplica\n")
                    self.txt_results.insert(tk.END, "   (La linearización describe el comportamiento local)\n")
                
                # Classify equilibrium
                classification = self._classify_equilibrium(eigenvalues, is_hyperbolic)
                stability = self._determine_stability(eigenvalues)
                
                self.txt_results.insert(tk.END, f"\nClasificación: {classification}\n")
                self.txt_results.insert(tk.END, f"Estabilidad: {stability}\n")
                
                # Show eigenvectors for hyperbolic points
                if is_hyperbolic and np.isreal(eigenvalues[0]) and np.isreal(eigenvalues[1]):
                    self.txt_results.insert(tk.END, f"\nAutovectores:\n")
                    for j, eigvec in enumerate(eigenvectors.T):
                        if np.isreal(eigvec[0]) and np.isreal(eigvec[1]):
                            self.txt_results.insert(tk.END, f"  v{j+1} = [{eigvec[0].real:.4f}, {eigvec[1].real:.4f}]\n")
                
                # Store classification with point
                self.equilibrium_points[i] = (x_eq, y_eq, classification, eigenvalues, eigenvectors, is_hyperbolic)
                
            except Exception as e:
                self.txt_results.insert(tk.END, f"Error al analizar: {str(e)}\n")
            
            self.txt_results.insert(tk.END, "\n")
    
    def _is_hyperbolic(self, eigenvalues):
        """
        Check if equilibrium point is hyperbolic.
        A point is hyperbolic if all eigenvalues have non-zero real parts.
        """
        tolerance = 1e-8
        for eig in eigenvalues:
            if abs(eig.real) < tolerance:
                return False
        return True
            
    def _classify_equilibrium(self, eigenvalues, is_hyperbolic=True):
        """Classify equilibrium point based on eigenvalues."""
        lambda1, lambda2 = eigenvalues
        
        # Check if eigenvalues are real or complex
        if np.isreal(lambda1) and np.isreal(lambda2):
            # Real eigenvalues
            if lambda1 * lambda2 > 0:
                if lambda1 > 0:
                    return "Nodo inestable (fuente) - Hiperbólico" if is_hyperbolic else "Nodo inestable (fuente)"
                else:
                    return "Nodo estable (sumidero) - Hiperbólico" if is_hyperbolic else "Nodo estable (sumidero)"
            elif lambda1 * lambda2 < 0:
                return "Punto silla - Hiperbólico" if is_hyperbolic else "Punto silla"
            else:
                # One eigenvalue is zero - non-hyperbolic
                return "NO Hiperbólico (λ = 0)"
        else:
            # Complex eigenvalues
            real_part = lambda1.real
            if abs(real_part) < 1e-8:
                return "Centro - NO Hiperbólico (Re(λ) = 0)"
            elif real_part > 0:
                return "Foco inestable (espiral divergente) - Hiperbólico" if is_hyperbolic else "Foco inestable"
            else:
                return "Foco estable (espiral convergente) - Hiperbólico" if is_hyperbolic else "Foco estable"
                
    def _determine_stability(self, eigenvalues):
        """Determine stability based on eigenvalues."""
        real_parts = [eig.real for eig in eigenvalues]
        
        if all(rp < 0 for rp in real_parts):
            return "Asintóticamente estable"
        elif all(rp <= 0 for rp in real_parts) and any(rp == 0 for rp in real_parts):
            return "Marginalmente estable (requiere análisis adicional)"
        else:
            return "Inestable"
            
    def _plot_phase_portrait(self):
        """Plot the phase portrait."""
        # Clear previous plots
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        
        # Create figure
        fig = Figure(figsize=(12, 10))
        
        # Phase portrait
        ax1 = fig.add_subplot(111)
        
        # Get plot ranges
        x_min, x_max = self.x_min.get(), self.x_max.get()
        y_min, y_max = self.y_min.get(), self.y_max.get()
        
        # Create grid
        density = self.grid_density.get()
        x_grid = np.linspace(x_min, x_max, density)
        y_grid = np.linspace(y_min, y_max, density)
        X, Y = np.meshgrid(x_grid, y_grid)
        
        # Evaluate vector field
        x, y = sp.symbols('x y')
        f_x = sp.lambdify((x, y), self.current_system[0], 'numpy')
        f_y = sp.lambdify((x, y), self.current_system[1], 'numpy')
        
        U = np.zeros_like(X)
        V = np.zeros_like(Y)
        
        for i in range(density):
            for j in range(density):
                try:
                    U[i, j] = f_x(X[i, j], Y[i, j])
                    V[i, j] = f_y(X[i, j], Y[i, j])
                except:
                    U[i, j] = 0
                    V[i, j] = 0
        
        # Plot vector field
        if self.show_vector_field.get():
            speed = np.sqrt(U**2 + V**2)
            speed[speed == 0] = 1  # Avoid division by zero
            U_norm = U / speed
            V_norm = V / speed
            
            ax1.quiver(X, Y, U_norm, V_norm, speed, cmap='viridis', alpha=0.6, 
                      scale=density*1.2, width=0.003, headwidth=4, headlength=5)
        
        # Plot nullclines
        if self.show_nullclines.get():
            try:
                # x' = 0 nullcline
                ax1.contour(X, Y, U, levels=[0], colors='red', linewidths=1.5, alpha=0.7)
                # y' = 0 nullcline
                ax1.contour(X, Y, V, levels=[0], colors='blue', linewidths=1.5, alpha=0.7)
                
                # Add legend for nullclines
                from matplotlib.lines import Line2D
                legend_elements = [
                    Line2D([0], [0], color='red', lw=1.5, label="x' = 0"),
                    Line2D([0], [0], color='blue', lw=1.5, label="y' = 0")
                ]
                ax1.legend(handles=legend_elements, loc='upper right', fontsize=9)
            except:
                pass
        
        # Plot equilibrium points
        if self.show_equilibria.get() and self.equilibrium_points:
            for eq_data in self.equilibrium_points:
                x_eq, y_eq = eq_data[0], eq_data[1]
                classification = eq_data[2] if len(eq_data) > 2 else "Desconocido"
                is_hyperbolic = eq_data[5] if len(eq_data) > 5 else True
                
                # Color and marker based on stability and hyperbolic status
                if "NO Hiperbólico" in classification or "NO hiperbólico" in classification.lower():
                    color = 'purple'
                    marker = 'D'  # Diamond for non-hyperbolic
                    size = 12
                elif "estable" in classification.lower() and "inestable" not in classification.lower():
                    color = 'green'
                    marker = 'o'
                    size = 10
                elif "silla" in classification.lower():
                    color = 'orange'
                    marker = 's'
                    size = 10
                else:
                    color = 'red'
                    marker = 'o'
                    size = 10
                
                ax1.plot(x_eq, y_eq, marker=marker, markersize=size, color=color, 
                        markeredgecolor='black', markeredgewidth=1.5, zorder=5)
                
                # Label with classification
                label_text = f'({x_eq:.2f}, {y_eq:.2f})'
                if "NO Hiperbólico" in classification:
                    label_text += '\n[NO Hip.]'
                
                ax1.text(x_eq, y_eq + 0.15, label_text, fontsize=8, ha='center',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        # Plot separatrices for saddle points
        if self.show_separatrices.get() and self.equilibrium_points:
            self._plot_separatrices(ax1, f_x, f_y)
        
        # Plot some sample trajectories
        self._plot_sample_trajectories(ax1, f_x, f_y)
        
        ax1.set_xlim(x_min, x_max)
        ax1.set_ylim(y_min, y_max)
        ax1.set_xlabel('x', fontsize=12)
        ax1.set_ylabel('y', fontsize=12)
        ax1.set_title('Retrato de Fase del Sistema No Lineal', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=0, color='k', linewidth=0.5)
        ax1.axvline(x=0, color='k', linewidth=0.5)
        
        # Add canvas
        canvas = FigureCanvasTkAgg(fig, master=self.right_panel)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Bind click event for interactive trajectories
        if self.click_cid:
            canvas.mpl_disconnect(self.click_cid)
        self.click_cid = canvas.mpl_connect('button_press_event', 
                                            lambda event: self._on_click(event, ax1, f_x, f_y, canvas))
        
        fig.tight_layout()
        
    def _plot_separatrices(self, ax, f_x, f_y):
        """Plot separatrices (stable/unstable manifolds) for saddle points."""
        for eq_data in self.equilibrium_points:
            if len(eq_data) < 3:
                continue
            
            x_eq, y_eq, classification = eq_data[0], eq_data[1], eq_data[2]
            
            if "silla" in classification.lower():
                eigenvalues = eq_data[3]
                eigenvectors = eq_data[4]
                
                # Find stable and unstable eigenvectors
                for i, eig in enumerate(eigenvalues):
                    if np.isreal(eig):
                        eigvec = eigenvectors[:, i].real
                        
                        # Normalize
                        eigvec = eigvec / np.linalg.norm(eigvec)
                        
                        # Plot in both directions
                        for direction in [-1, 1]:
                            eps = 0.01
                            x0 = x_eq + direction * eps * eigvec[0]
                            y0 = y_eq + direction * eps * eigvec[1]
                            
                            # Determine color based on eigenvalue sign
                            if eig.real < 0:  # Stable direction - integrate backward
                                t = np.linspace(0, -self.t_max.get(), 300)  # Reduced from 1000
                                color = 'cyan'
                                linewidth = 2
                            else:  # Unstable direction - integrate forward
                                t = np.linspace(0, self.t_max.get(), 300)  # Reduced from 1000
                                color = 'magenta'
                                linewidth = 2
                            
                            try:
                                def system(state, t):
                                    x, y = state
                                    try:
                                        dx = f_x(x, y)
                                        dy = f_y(x, y)
                                        dx = float(dx) if np.isscalar(dx) else float(dx[0]) if hasattr(dx, '__len__') else 0.0
                                        dy = float(dy) if np.isscalar(dy) else float(dy[0]) if hasattr(dy, '__len__') else 0.0
                                        if not np.isfinite(dx):
                                            dx = 0.0
                                        if not np.isfinite(dy):
                                            dy = 0.0
                                        return [dx, dy]
                                    except:
                                        return [0.0, 0.0]
                                
                                sol = odeint(system, [x0, y0], t)
                                
                                # Filter valid points
                                if len(sol) > 1:
                                    valid_mask = np.isfinite(sol[:, 0]) & np.isfinite(sol[:, 1])
                                    if np.any(valid_mask):
                                        sol_valid = sol[valid_mask]
                                        if len(sol_valid) > 1:
                                            ax.plot(sol_valid[:, 0], sol_valid[:, 1], color=color, linewidth=linewidth, 
                                                   alpha=0.7, linestyle='--')
                            except:
                                pass
                                
    def _plot_sample_trajectories(self, ax, f_x, f_y):
        """Plot some random sample trajectories."""
        # Random initial conditions - reduced number
        num_traj = min(self.num_trajectories.get(), 8)
        
        x_min, x_max = self.x_min.get(), self.x_max.get()
        y_min, y_max = self.y_min.get(), self.y_max.get()
        
        np.random.seed(42)  # For reproducibility
        
        for _ in range(num_traj):
            x0 = np.random.uniform(x_min, x_max)
            y0 = np.random.uniform(y_min, y_max)
            
            self._plot_trajectory(ax, f_x, f_y, x0, y0, color='gray', alpha=0.3, linewidth=0.8)
            
    def _plot_trajectory(self, ax, f_x, f_y, x0, y0, color='blue', alpha=0.8, linewidth=1.5):
        """Plot a single trajectory from initial condition (x0, y0)."""
        t_max = self.t_max.get()
        direction = self.trajectory_direction.get()
        
        def system(state, t):
            x, y = state
            try:
                dx = f_x(x, y)
                dy = f_y(x, y)
                # Convert to float and check validity
                dx = float(dx) if np.isscalar(dx) else float(dx[0]) if hasattr(dx, '__len__') else 0.0
                dy = float(dy) if np.isscalar(dy) else float(dy[0]) if hasattr(dy, '__len__') else 0.0
                
                # Check for NaN or infinity
                if not np.isfinite(dx):
                    dx = 0.0
                if not np.isfinite(dy):
                    dy = 0.0
                    
                return [dx, dy]
            except:
                return [0.0, 0.0]
        
        # Forward integration - reduced points
        if direction in ["forward", "both"]:
            t_forward = np.linspace(0, t_max, 200)  # Reduced from 500
            try:
                sol_forward = odeint(system, [x0, y0], t_forward)
                
                # Check if solution is valid
                if len(sol_forward) > 1:
                    # Filter out any invalid points
                    valid_mask = np.isfinite(sol_forward[:, 0]) & np.isfinite(sol_forward[:, 1])
                    if np.any(valid_mask):
                        sol_valid = sol_forward[valid_mask]
                        if len(sol_valid) > 1:
                            ax.plot(sol_valid[:, 0], sol_valid[:, 1], color=color, alpha=alpha, 
                                   linewidth=linewidth, zorder=3)
            except:
                pass
        
        # Backward integration - reduced points
        if direction in ["backward", "both"]:
            t_backward = np.linspace(0, -t_max, 200)  # Reduced from 500
            try:
                sol_backward = odeint(system, [x0, y0], t_backward)
                
                # Check if solution is valid
                if len(sol_backward) > 1:
                    # Filter out any invalid points
                    valid_mask = np.isfinite(sol_backward[:, 0]) & np.isfinite(sol_backward[:, 1])
                    if np.any(valid_mask):
                        sol_valid = sol_backward[valid_mask]
                        if len(sol_valid) > 1:
                            ax.plot(sol_valid[:, 0], sol_valid[:, 1], color=color, alpha=alpha, 
                                   linewidth=linewidth, linestyle='--', zorder=3)
            except:
                pass
        
        # Mark initial point
        try:
            ax.plot(x0, y0, 'o', color=color, markersize=6, markeredgecolor='black', 
                   markeredgewidth=0.5, zorder=4)
        except:
            pass
        
    def _on_click(self, event, ax, f_x, f_y, canvas):
        """Handle click event to plot trajectory from clicked point."""
        # Validate click is in the axes
        if event.inaxes != ax:
            return
        
        # Get coordinates
        x0, y0 = event.xdata, event.ydata
        
        # Validate coordinates are not None and are finite
        if x0 is None or y0 is None:
            return
        
        if not np.isfinite(x0) or not np.isfinite(y0):
            return
        
        # Check if coordinates are within plot bounds
        x_min, x_max = self.x_min.get(), self.x_max.get()
        y_min, y_max = self.y_min.get(), self.y_max.get()
        
        if not (x_min <= x0 <= x_max and y_min <= y0 <= y_max):
            return
        
        # Store clicked trajectory
        self.clicked_trajectories.append((x0, y0))
        
        try:
            # Plot trajectory
            self._plot_trajectory(ax, f_x, f_y, x0, y0, color='red', alpha=0.9, linewidth=2)
            
            # Redraw canvas
            canvas.draw_idle()
        except Exception as e:
            print(f"Error plotting trajectory: {e}")
            # Remove the failed trajectory from list
            if self.clicked_trajectories and self.clicked_trajectories[-1] == (x0, y0):
                self.clicked_trajectories.pop()
        
    def clear_clicked_trajectories(self):
        """Clear clicked trajectories and replot."""
        self.clicked_trajectories = []
        if self.current_system:
            try:
                self._plot_phase_portrait()
            except Exception as e:
                print(f"Error reploting: {e}")
            
    def clear_plots(self):
        """Clear all plots."""
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        self.clicked_trajectories = []
        if self.click_cid:
            try:
                # Note: click_cid will be recreated on next plot
                self.click_cid = None
            except:
                pass


def main():
    root = tk.Tk()
    app = NonlinearSystem2DApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
