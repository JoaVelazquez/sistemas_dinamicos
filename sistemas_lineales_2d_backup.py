#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistemas Dinámicos Lineales 2D - Análisis de Nodos y Clasificación
Basado en la estructura del analizador de bifurcaciones
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import sympy as sp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

mpl.rcParams.update({
    "figure.dpi": 100,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "legend.fontsize": 10,
})

class LinearSystem2DApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistemas Dinámicos Lineales 2D - Análisis de Nodos v1.1")
        self.geometry("1400x900")
        
        # Theme color (matching launcher card)
        self.theme_color = "#3498db"  # Blue for Linear Systems
        self.theme_color_light = "#5dade2"
        self.theme_color_dark = "#2874a6"
        
        # Variables for the system x' = Ax (matrix form)
        self.a11 = tk.DoubleVar(value=1.0)  # dx/dt = a11*x + a12*y
        self.a12 = tk.DoubleVar(value=0.0)
        self.a21 = tk.DoubleVar(value=0.0)  # dy/dt = a21*x + a22*y
        self.a22 = tk.DoubleVar(value=-1.0)
        
        # Variables for direct equation input
        self.x_prime_str = tk.StringVar(value="x")  # x' = 
        self.y_prime_str = tk.StringVar(value="-y")  # y' = 
        self.input_mode = tk.StringVar(value="matrix")  # "matrix" or "equations"
        
        # Forcing functions for non-homogeneous systems
        self.f1_str = tk.StringVar(value="0")  # f₁(t) for x' equation
        self.f2_str = tk.StringVar(value="0")  # f₂(t) for y' equation
        self.use_forcing = tk.BooleanVar(value=False)
        
        # Plot parameters
        self.x_min = tk.DoubleVar(value=-3.0)
        self.x_max = tk.DoubleVar(value=3.0)
        self.y_min = tk.DoubleVar(value=-3.0)
        self.y_max = tk.DoubleVar(value=3.0)
        self.time_max = tk.DoubleVar(value=5.0)
        
        # Poincaré map parameter
        self.poincare_dt = tk.DoubleVar(value=0.5)
        
        # Interactive trajectory options
        self.trajectory_direction = tk.StringVar(value="forward")  # "forward", "backward", "both"
        self.clicked_trajectories = []
        self.click_cid = None
        
        # Exercise selector
        self.exercise_var = tk.StringVar(value="Manual")
        
        # Predefined exercises from the image
        self.exercises = {
            "1. x'=x, y'=y": {"a11": 1, "a12": 0, "a21": 0, "a22": 1},
            "2. x'=-y, y'=x": {"a11": 0, "a12": -1, "a21": 1, "a22": 0},
            "3. x'=x, y'=-y": {"a11": 1, "a12": 0, "a21": 0, "a22": -1},
            "4. x'=y-x, y'=-y-x": {"a11": -1, "a12": 1, "a21": -1, "a22": -1},
            "5. x'=x+y, y'=x+y": {"a11": 1, "a12": 1, "a21": 1, "a22": 1},
            "6. x'=-y, y'=x": {"a11": 0, "a12": -1, "a21": 1, "a22": 0},
            "7. x'=2y, y'=2x": {"a11": 0, "a12": 2, "a21": 2, "a22": 0},
            "8. x'=-y+x, y'=x+y": {"a11": 1, "a12": -1, "a21": 1, "a22": 1},
            "9. x'=x-2y, y'=-2x+y": {"a11": 1, "a12": -2, "a21": -2, "a22": 1},
            "10. x'=x+2y, y'=3y+4x": {"a11": 1, "a12": 2, "a21": 4, "a22": 3},
            "11. x'=x-2y, y'=x+y": {"a11": 1, "a12": -2, "a21": 1, "a22": 1},
            "12. x'=x-y, y'=3x+3y": {"a11": 1, "a12": -1, "a21": 3, "a22": 3},
            "13. x'=-4x+3y, y'=-6x+5y": {"a11": -4, "a12": 3, "a21": -6, "a22": 5},
            "14. x'=6x-y, y'=5x+4y": {"a11": 6, "a12": -1, "a21": 5, "a22": 4},
            "15. x'=x+2y, y'=2x-4y": {"a11": 1, "a12": 2, "a21": 2, "a22": -4},
            "16. x'=2x-5y, y'=4x-2y": {"a11": 2, "a12": -5, "a21": 4, "a22": -2},
            "17. x'=-5x+2y, y'=-10x+3y": {"a11": -5, "a12": 2, "a21": -10, "a22": 3},
            "18. x'=-2x+3y, y'=-6x+4y": {"a11": -2, "a12": 3, "a21": -6, "a22": 4},
            "19. x'=5x-4y, y'=x+y": {"a11": 5, "a12": -4, "a21": 1, "a22": 1},
            "20. x'=3x+y, y'=x+3y": {"a11": 3, "a12": 1, "a21": 1, "a22": 3},
            "21. x'=y, y'=6x+y": {"a11": 0, "a12": 1, "a21": 6, "a22": 1},
            "22. x'=2x-2y, y'=4x-2y": {"a11": 2, "a12": -2, "a21": 4, "a22": -2},
            "23. x'=x+2y, y'=2x+y": {"a11": 1, "a12": 2, "a21": 2, "a22": 1},
            "24. x'=2x+3y, y'=2x+y": {"a11": 2, "a12": 3, "a21": 2, "a22": 1},
            "25. x'=-3x-4y, y'=2x+y": {"a11": -3, "a12": -4, "a21": 2, "a22": 1},
            "26. x'=3x-y, y'=9x-3y": {"a11": 3, "a12": -1, "a21": 9, "a22": -3},
            "27. x'=-2x+y, y'=x-2y": {"a11": -2, "a12": 1, "a21": 1, "a22": -2},
            "28. x'=x+3y, y'=x-y": {"a11": 1, "a12": 3, "a21": 1, "a22": -1},
        }
        
        # Storage for current analysis
        self._current_matrix = None
        self._current_eigenvalues = None
        self._current_eigenvectors = None
        self._current_classification = None
        
        self._build_ui()
        self._load_exercise("1. x'=x, y'=y")  # Load first exercise by default

    def _build_ui(self):
        """Build the main UI with left panel for controls and right panel for plots."""
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
        
        # Create main horizontal layout
        main_paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Left panel for inputs and results
        self.left_panel = ttk.Frame(main_paned)
        main_paned.add(self.left_panel, weight=1)
        
        # Right panel for plots
        self.right_panel = ttk.Frame(main_paned)
        main_paned.add(self.right_panel, weight=2)
        
        # Create content
        self._create_left_panel_content()
        self._create_right_panel_content()
        
        # Status bar
        self._create_status_bar()

    def _create_left_panel_content(self):
        """Create the left panel with exercises, matrix input, and results."""
        # Exercise selector
        self._create_exercise_selector()
        
        # Matrix input
        self._create_matrix_input()
        
        # Control buttons
        self._create_control_buttons()
        
        # Results display
        self._create_results_display()

    def _create_exercise_selector(self):
        """Create exercise selection dropdown."""
        exercise_frame = ttk.LabelFrame(self.left_panel, text="Ejercicios Predefinidos")
        exercise_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(8, 4))
        
        # Dropdown for exercises
        ttk.Label(exercise_frame, text="Seleccionar ejercicio:").pack(anchor="w", padx=8, pady=(8, 4))
        
        exercise_combo = ttk.Combobox(exercise_frame, textvariable=self.exercise_var, width=35)
        exercise_combo['values'] = ["Manual"] + list(self.exercises.keys())
        exercise_combo.pack(fill=tk.X, padx=8, pady=(0, 8))
        exercise_combo.bind('<<ComboboxSelected>>', self._on_exercise_selected)

    def _create_matrix_input(self):
        """Create matrix input section with mode selection."""
        matrix_frame = ttk.LabelFrame(self.left_panel, text="Definición del Sistema")
        matrix_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        
        # Mode selection
        mode_frame = ttk.Frame(matrix_frame)
        mode_frame.pack(fill=tk.X, padx=8, pady=(8, 4))
        
        ttk.Label(mode_frame, text="Modo de entrada:").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Matriz A", variable=self.input_mode, 
                       value="matrix", command=self._on_mode_change).pack(side=tk.LEFT, padx=(8, 4))
        ttk.Radiobutton(mode_frame, text="Ecuaciones directas", variable=self.input_mode, 
                       value="equations", command=self._on_mode_change).pack(side=tk.LEFT, padx=4)
        
        # Container for input methods
        self.input_container = ttk.Frame(matrix_frame)
        self.input_container.pack(fill=tk.X, padx=8, pady=4)
        
        # Create both input methods
        self._create_matrix_mode()
        self._create_equations_mode()
        
        # Plot parameters
        params_frame = ttk.LabelFrame(matrix_frame, text="Parámetros de Graficación")
        params_frame.pack(fill=tk.X, padx=8, pady=(8, 8))
        
        # Range inputs
        ttk.Label(params_frame, text="Rango x:").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        tk.Entry(params_frame, textvariable=self.x_min, width=6).grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(params_frame, text="a").grid(row=0, column=2, padx=2)
        tk.Entry(params_frame, textvariable=self.x_max, width=6).grid(row=0, column=3, padx=2, pady=2)
        
        ttk.Label(params_frame, text="Rango y:").grid(row=1, column=0, sticky="w", padx=4, pady=2)
        tk.Entry(params_frame, textvariable=self.y_min, width=6).grid(row=1, column=1, padx=2, pady=2)
        ttk.Label(params_frame, text="a").grid(row=1, column=2, padx=2)
        tk.Entry(params_frame, textvariable=self.y_max, width=6).grid(row=1, column=3, padx=2, pady=2)
        
        ttk.Label(params_frame, text="Tiempo máx:").grid(row=2, column=0, sticky="w", padx=4, pady=2)
        tk.Entry(params_frame, textvariable=self.time_max, width=6).grid(row=2, column=1, padx=2, pady=2)
        
        # Forcing functions for non-homogeneous systems
        forcing_frame = ttk.LabelFrame(matrix_frame, text="Funciones de Forzamiento (Opcional)")
        forcing_frame.pack(fill=tk.X, padx=8, pady=(8, 8))
        
        # Enable forcing checkbox
        ttk.Checkbutton(forcing_frame, text="Activar sistema no homogéneo: x' = Ax + f(t)", 
                       variable=self.use_forcing,
                       command=self._toggle_forcing).pack(anchor="w", padx=4, pady=4)
        
        # Forcing function inputs
        self.forcing_inputs_frame = ttk.Frame(forcing_frame)
        self.forcing_inputs_frame.pack(fill=tk.X, padx=4, pady=4)
        
        # f₁(t) for x' equation
        f1_frame = ttk.Frame(self.forcing_inputs_frame)
        f1_frame.pack(fill=tk.X, pady=2)
        ttk.Label(f1_frame, text="f₁(t) =", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(f1_frame, textvariable=self.f1_str, width=25, font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # f₂(t) for y' equation
        f2_frame = ttk.Frame(self.forcing_inputs_frame)
        f2_frame.pack(fill=tk.X, pady=2)
        ttk.Label(f2_frame, text="f₂(t) =", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(f2_frame, textvariable=self.f2_str, width=25, font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Help text for forcing
        help_text = "Ejemplos: sin(t), cos(2*t), exp(-t), t, t**2, 5 (constante)"
        ttk.Label(self.forcing_inputs_frame, text=help_text, font=("Arial", 8), foreground="gray").pack(anchor="w", pady=(4, 0))
        
        # Initially disable forcing inputs
        self._toggle_forcing()
        
        # Show initial mode
        self._on_mode_change()

    def _toggle_forcing(self):
        """Enable/disable forcing function inputs."""
        state = 'normal' if self.use_forcing.get() else 'disabled'
        for widget in self.forcing_inputs_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Entry):
                        child.config(state=state)

    def _create_matrix_mode(self):
        """Create matrix input widgets."""
        self.matrix_mode_frame = ttk.Frame(self.input_container)
        
        # Create 2x2 matrix input grid
        ttk.Label(self.matrix_mode_frame, text="x' = Ax, donde A =", font=("Arial", 11)).grid(row=0, column=0, columnspan=5, pady=(0, 8))
        
        # Left bracket
        ttk.Label(self.matrix_mode_frame, text="[", font=("Arial", 16)).grid(row=1, column=0, pady=4)
        
        # Matrix elements
        tk.Entry(self.matrix_mode_frame, textvariable=self.a11, width=8, justify='center').grid(row=1, column=1, padx=2, pady=4)
        tk.Entry(self.matrix_mode_frame, textvariable=self.a12, width=8, justify='center').grid(row=1, column=2, padx=2, pady=4)
        
        # Right bracket for first row
        ttk.Label(self.matrix_mode_frame, text="]", font=("Arial", 16)).grid(row=1, column=3, pady=4)
        
        # Second row
        ttk.Label(self.matrix_mode_frame, text="", font=("Arial", 16)).grid(row=2, column=0, pady=2)
        tk.Entry(self.matrix_mode_frame, textvariable=self.a21, width=8, justify='center').grid(row=2, column=1, padx=2, pady=2)
        tk.Entry(self.matrix_mode_frame, textvariable=self.a22, width=8, justify='center').grid(row=2, column=2, padx=2, pady=2)

    def _create_equations_mode(self):
        """Create direct equation input widgets."""
        self.equations_mode_frame = ttk.Frame(self.input_container)
        
        ttk.Label(self.equations_mode_frame, text="Ingresa las ecuaciones directamente:", font=("Arial", 11)).pack(anchor="w", pady=(0, 8))
        
        # x' equation
        x_frame = ttk.Frame(self.equations_mode_frame)
        x_frame.pack(fill=tk.X, pady=4)
        ttk.Label(x_frame, text="x' =", font=("Arial", 12)).pack(side=tk.LEFT)
        x_entry = tk.Entry(x_frame, textvariable=self.x_prime_str, width=35, font=("Arial", 11))
        x_entry.pack(side=tk.LEFT, padx=(8, 0), fill=tk.X, expand=True)
        x_entry.bind("<KeyRelease>", self._on_equation_change)
        
        # y' equation  
        y_frame = ttk.Frame(self.equations_mode_frame)
        y_frame.pack(fill=tk.X, pady=4)
        ttk.Label(y_frame, text="y' =", font=("Arial", 12)).pack(side=tk.LEFT)
        y_entry = tk.Entry(y_frame, textvariable=self.y_prime_str, width=35, font=("Arial", 11))
        y_entry.pack(side=tk.LEFT, padx=(8, 0), fill=tk.X, expand=True)
        y_entry.bind("<KeyRelease>", self._on_equation_change)
        
        # Mathematical keyboard for equations
        self._create_math_keyboard_compact(self.equations_mode_frame)
        
        # Help text
        help_frame = ttk.Frame(self.equations_mode_frame)
        help_frame.pack(fill=tk.X, pady=(8, 0))
        help_text = "Usa 'x' e 'y' para las variables. Ejemplo: x' = 2*x - 3*y, y' = x + y"
        ttk.Label(help_frame, text=help_text, font=("Arial", 9), foreground="gray").pack(anchor="w")

    def _create_math_keyboard_compact(self, parent):
        """Create a compact mathematical keyboard for equation input."""
        kb_frame = ttk.LabelFrame(parent, text="Teclado Matemático")
        kb_frame.pack(fill=tk.X, pady=(8, 0))
        
        button_frame = ttk.Frame(kb_frame)
        button_frame.pack(padx=8, pady=4)
        
        # Compact set of useful mathematical symbols
        keys = ["x", "y", "+", "-", "*", "/", "(", ")", "^", "sin(", "cos(", "exp(", "log(", "sqrt("]
        
        for i, k in enumerate(keys):
            row = i // 7
            col = i % 7
            btn = ttk.Button(button_frame, text=k, width=4,
                           command=lambda key=k: self._insert_math_token(key))
            btn.grid(row=row, column=col, padx=1, pady=1)

    def _insert_math_token(self, token):
        """Insert mathematical token into the focused equation field."""
        # Get the currently focused widget
        focused = self.focus_get()
        
        # Check if it's one of our equation entry fields
        if hasattr(focused, 'get') and hasattr(focused, 'insert'):
            current_pos = focused.index(tk.INSERT)
            focused.insert(current_pos, token)
            self._on_equation_change()

    def _on_mode_change(self):
        """Handle input mode change."""
        # Hide all frames first
        self.matrix_mode_frame.pack_forget()
        self.equations_mode_frame.pack_forget()
        
        # Show the selected mode
        if self.input_mode.get() == "matrix":
            self.matrix_mode_frame.pack(fill=tk.X, pady=4)
        else:
            self.equations_mode_frame.pack(fill=tk.X, pady=4)

    def _on_equation_change(self, event=None):
        """Handle equation text change - try to parse and update matrix."""
        if self.input_mode.get() == "equations":
            try:
                self._parse_equations_to_matrix()
            except Exception:
                pass  # Don't show errors while typing

    def _parse_equations_to_matrix(self):
        """Parse the equation strings and extract the matrix coefficients."""
        import sympy as sp
        
        x, y = sp.symbols('x y')
        
        try:
            # Parse the equations
            x_prime_expr = sp.sympify(self.x_prime_str.get())
            y_prime_expr = sp.sympify(self.y_prime_str.get())
            
            # Extract coefficients (assuming linear system)
            # x' = a11*x + a12*y + constant_terms
            # y' = a21*x + a22*y + constant_terms
            
            # Get coefficients
            a11 = float(x_prime_expr.coeff(x, 1) or 0)
            a12 = float(x_prime_expr.coeff(y, 1) or 0)
            a21 = float(y_prime_expr.coeff(x, 1) or 0)
            a22 = float(y_prime_expr.coeff(y, 1) or 0)
            
            # Update matrix variables
            self.a11.set(a11)
            self.a12.set(a12)
            self.a21.set(a21)
            self.a22.set(a22)
            
        except Exception as e:
            # If parsing fails, don't update matrix
            pass

    def _create_quick_examples(self):
        """Create quick example buttons."""
        examples_frame = ttk.LabelFrame(self.left_panel, text="📚 Ejemplos Rápidos")
        examples_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        
        # Row 1: Basic types
        row1_frame = ttk.Frame(examples_frame)
        row1_frame.pack(fill=tk.X, padx=4, pady=2)
        
        tk.Button(row1_frame, text="Nodo Estable\n(Atractor)", 
                  command=lambda: self._load_example_system(-1, 0, 0, -2),
                  bg=self.theme_color, fg='white',
                  activebackground=self.theme_color_light,
                  font=("Arial", 8, "bold"),
                  relief=tk.RAISED, bd=2, cursor='hand2',
                  width=12, height=2).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        tk.Button(row1_frame, text="Nodo Inestable\n(Repulsor)", 
                  command=lambda: self._load_example_system(1, 0, 0, 2),
                  bg=self.theme_color, fg='white',
                  activebackground=self.theme_color_light,
                  font=("Arial", 8, "bold"),
                  relief=tk.RAISED, bd=2, cursor='hand2',
                  width=12, height=2).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        tk.Button(row1_frame, text="Espiral Estable\n(Sumidero)", 
                  command=lambda: self._load_example_system(-1, -2, 2, -1),
                  bg=self.theme_color, fg='white',
                  activebackground=self.theme_color_light,
                  font=("Arial", 8, "bold"),
                  relief=tk.RAISED, bd=2, cursor='hand2',
                  width=12, height=2).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Row 2: More types
        row2_frame = ttk.Frame(examples_frame)
        row2_frame.pack(fill=tk.X, padx=4, pady=2)
        
        tk.Button(row2_frame, text="Espiral Inestable\n(Fuente)", 
                  command=lambda: self._load_example_system(1, 2, -2, 1),
                  bg=self.theme_color, fg='white',
                  activebackground=self.theme_color_light,
                  font=("Arial", 8, "bold"),
                  relief=tk.RAISED, bd=2, cursor='hand2',
                  width=12, height=2).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        tk.Button(row2_frame, text="Centro\n(Órbitas)", 
                  command=lambda: self._load_example_system(0, -1, 1, 0),
                  bg=self.theme_color, fg='white',
                  activebackground=self.theme_color_light,
                  font=("Arial", 8, "bold"),
                  relief=tk.RAISED, bd=2, cursor='hand2',
                  width=12, height=2).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        tk.Button(row2_frame, text="Punto Silla\n(Hiperbólico)", 
                  command=lambda: self._load_example_system(1, 0, 0, -1),
                  bg=self.theme_color, fg='white',
                  activebackground=self.theme_color_light,
                  font=("Arial", 8, "bold"),
                  relief=tk.RAISED, bd=2, cursor='hand2',
                  width=12, height=2).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
    
    def _load_example_system(self, a11, a12, a21, a22):
        """Load an example system."""
        self.input_mode.set("matrix")
        self._toggle_input_mode()
        self.a11.set(a11)
        self.a12.set(a12)
        self.a21.set(a21)
        self.a22.set(a22)

    def _create_control_buttons(self):
        """Create control buttons."""
        # Quick examples
        self._create_quick_examples()
        
        # Trajectory control section
        traj_frame = ttk.LabelFrame(self.left_panel, text="Trayectorias Interactivas")
        traj_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        
        ttk.Label(traj_frame, text="Haz clic en el retrato de fase para graficar trayectorias", 
                 font=("Arial", 9, "italic"), foreground="blue").pack(anchor="w", padx=8, pady=(4, 2))
        
        # Trajectory direction
        ttk.Label(traj_frame, text="Dirección de integración:").pack(anchor="w", padx=8, pady=(4, 2))
        dir_frame = ttk.Frame(traj_frame)
        dir_frame.pack(fill=tk.X, padx=8, pady=2)
        ttk.Radiobutton(dir_frame, text="Adelante", variable=self.trajectory_direction, value="forward").pack(anchor="w", padx=16)
        ttk.Radiobutton(dir_frame, text="Atrás", variable=self.trajectory_direction, value="backward").pack(anchor="w", padx=16)
        ttk.Radiobutton(dir_frame, text="Ambas", variable=self.trajectory_direction, value="both").pack(anchor="w", padx=16)
        
        ttk.Button(traj_frame, text="Limpiar Trayectorias Click", 
                  command=self.clear_clicked_trajectories).pack(fill=tk.X, padx=8, pady=(4, 8))
        
        # Main action buttons
        button_frame = ttk.LabelFrame(self.left_panel, text="Acciones")
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        
        ttk.Button(button_frame, text="Analizar Sistema", command=self.analyze_system).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(button_frame, text="Limpiar Gráficos", command=self.clear_plots).pack(fill=tk.X, padx=8, pady=4)

    def _create_results_display(self):
        """Create results display area."""
        results_frame = ttk.LabelFrame(self.left_panel, text="Análisis del Sistema")
        results_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)
        
        self.txt_results = ScrolledText(results_frame, wrap='word', font=("Consolas", 10))
        self.txt_results.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        self._write_results_header()

    def _create_right_panel_content(self):
        """Create the right panel with plots."""
        # Create a canvas with scrollbar for the plots
        canvas_container = tk.Canvas(self.right_panel, borderwidth=0)
        scrollbar = ttk.Scrollbar(self.right_panel, orient="vertical", command=canvas_container.yview)
        self.scrollable_frame = ttk.Frame(canvas_container)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_container.configure(scrollregion=canvas_container.bbox("all"))
        )
        
        canvas_container.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas_container.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mouse wheel to scrolling
        def _on_mousewheel(event):
            canvas_container.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas_container.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Create vertical layout for multiple plots within scrollable frame
        plots_paned = ttk.Panedwindow(self.scrollable_frame, orient=tk.VERTICAL)
        plots_paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)
        
        # Phase portrait plot
        self._create_phase_portrait_panel(plots_paned)
        
        # Poincaré map plot
        self._create_poincare_panel(plots_paned)
        
        # Solution trajectories plot
        self._create_trajectories_panel(plots_paned)

    def _create_phase_portrait_panel(self, parent):
        """Create phase portrait panel."""
        phase_frame = ttk.LabelFrame(parent, text="Retrato de Fase")
        parent.add(phase_frame, weight=1)
        
        self.fig_phase, self.ax_phase, self.canvas_phase = self._create_figure_canvas(
            phase_frame, figsize=(7, 5)
        )
        self.canvas_phase.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=4, pady=4)

    def _create_poincare_panel(self, parent):
        """Create Poincaré map panel."""
        poincare_frame = ttk.LabelFrame(parent, text="Mapa de Poincaré")
        parent.add(poincare_frame, weight=1)
        
        # Add control for sampling interval
        control_frame = ttk.Frame(poincare_frame)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=4, pady=2)
        
        ttk.Label(control_frame, text="Intervalo de muestreo Δt:").pack(side=tk.LEFT, padx=4)
        tk.Entry(control_frame, textvariable=self.poincare_dt, width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(control_frame, text="💡 Puntos discretos del flujo temporal", 
                 font=("Arial", 9), foreground="blue").pack(side=tk.LEFT, padx=10)
        
        self.fig_poincare, self.ax_poincare, self.canvas_poincare = self._create_figure_canvas(
            poincare_frame, figsize=(7, 5)
        )
        self.canvas_poincare.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=4, pady=4)

    def _create_trajectories_panel(self, parent):
        """Create solution trajectories panel."""
        traj_frame = ttk.LabelFrame(parent, text="Trayectorias de Solución")
        parent.add(traj_frame, weight=1)
        
        self.fig_traj, self.ax_traj, self.canvas_traj = self._create_figure_canvas(
            traj_frame, figsize=(7, 3.5)
        )
        self.canvas_traj.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=4, pady=4)

    def _create_figure_canvas(self, parent, figsize):
        """Helper to create matplotlib figure and canvas."""
        fig = Figure(figsize=figsize)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=parent)
        return fig, ax, canvas

    def _create_status_bar(self):
        """Create status bar."""
        status_frame = ttk.Frame(self)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=6)
        self.status = tk.StringVar(value="Listo")
        ttk.Label(status_frame, textvariable=self.status).pack(side=tk.LEFT)

    def _write_results_header(self):
        """Write header in results display."""
        self.txt_results.config(state='normal')
        self.txt_results.delete('1.0', tk.END)
        self.txt_results.insert(tk.END, "== ANÁLISIS DE SISTEMAS LINEALES 2D ==\n\n")
        self.txt_results.insert(tk.END, "Para sistemas de la forma:\n")
        self.txt_results.insert(tk.END, "  x' = a₁₁x + a₁₂y\n")
        self.txt_results.insert(tk.END, "  y' = a₂₁x + a₂₂y\n\n")
        self.txt_results.insert(tk.END, "Opciones de entrada:\n")
        self.txt_results.insert(tk.END, "1. Selecciona un ejercicio predefinido\n")
        self.txt_results.insert(tk.END, "2. Ingresa la matriz A directamente\n")
        self.txt_results.insert(tk.END, "3. Escribe las ecuaciones x' e y' directamente\n\n")
        self.txt_results.insert(tk.END, "Presiona 'Analizar Sistema' para obtener:\n")
        self.txt_results.insert(tk.END, "• Autovalores y autovectores\n")
        self.txt_results.insert(tk.END, "• Clasificación del punto crítico\n")
        self.txt_results.insert(tk.END, "• Retrato de fase\n")
        self.txt_results.insert(tk.END, "• Trayectorias de solución\n")
        self.txt_results.config(state='disabled')

    def _on_exercise_selected(self, event=None):
        """Handle exercise selection."""
        exercise = self.exercise_var.get()
        if exercise != "Manual" and exercise in self.exercises:
            self._load_exercise(exercise)

    def _load_exercise(self, exercise_key):
        """Load a predefined exercise."""
        if exercise_key in self.exercises:
            params = self.exercises[exercise_key]
            self.a11.set(params["a11"])
            self.a12.set(params["a12"])
            self.a21.set(params["a21"])
            self.a22.set(params["a22"])
            self.exercise_var.set(exercise_key)
            
            # Also update equation strings to match the matrix
            self._update_equations_from_matrix()

    def _update_equations_from_matrix(self):
        """Update equation strings based on current matrix values."""
        a11, a12 = self.a11.get(), self.a12.get()
        a21, a22 = self.a21.get(), self.a22.get()
        
        # Build x' equation
        x_terms = []
        if a11 != 0:
            if a11 == 1:
                x_terms.append("x")
            elif a11 == -1:
                x_terms.append("-x")
            else:
                x_terms.append(f"{a11}*x")
        
        if a12 != 0:
            if a12 == 1:
                x_terms.append("y" if not x_terms else "+y")
            elif a12 == -1:
                x_terms.append("-y")
            else:
                sign = "+" if a12 > 0 and x_terms else ""
                x_terms.append(f"{sign}{a12}*y")
        
        x_eq = "".join(x_terms) if x_terms else "0"
        
        # Build y' equation
        y_terms = []
        if a21 != 0:
            if a21 == 1:
                y_terms.append("x")
            elif a21 == -1:
                y_terms.append("-x")
            else:
                y_terms.append(f"{a21}*x")
        
        if a22 != 0:
            if a22 == 1:
                y_terms.append("y" if not y_terms else "+y")
            elif a22 == -1:
                y_terms.append("-y")
            else:
                sign = "+" if a22 > 0 and y_terms else ""
                y_terms.append(f"{sign}{a22}*y")
        
        y_eq = "".join(y_terms) if y_terms else "0"
        
        self.x_prime_str.set(x_eq)
        self.y_prime_str.set(y_eq)

    def analyze_system(self):
        """Analyze the linear system."""
        try:
            # Get matrix elements
            A = np.array([
                [self.a11.get(), self.a12.get()],
                [self.a21.get(), self.a22.get()]
            ], dtype=float)
            
            print(f"DEBUG: Analyzing matrix A =\n{A}")  # DEBUG
            
            self._current_matrix = A.copy()
            
            # Calculate eigenvalues and eigenvectors
            eigenvals, eigenvecs = np.linalg.eig(A)
            self._current_eigenvalues = eigenvals.copy()
            self._current_eigenvectors = eigenvecs.copy()
            
            print(f"DEBUG: Eigenvalues = {eigenvals}")  # DEBUG
            print(f"DEBUG: Eigenvectors =\n{eigenvecs}")  # DEBUG
            
            # Classify the critical point
            classification = self._classify_critical_point(eigenvals)
            self._current_classification = classification
            
            print(f"DEBUG: Classification = {classification}")  # DEBUG
            
            # Update results display
            self._update_results(A, eigenvals, eigenvecs, classification)
            
            # Plot phase portrait
            self._plot_phase_portrait(A)
            
            # Plot Poincaré map
            self._plot_poincare_map(A)
            
            # Plot solution trajectories
            self._plot_solution_trajectories(A)
            
            self.status.set("Sistema analizado correctamente.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al analizar el sistema: {str(e)}")
            self.status.set("Error en el análisis.")

    def _classify_critical_point(self, eigenvals):
        """Classify the critical point based on eigenvalues."""
        lambda1, lambda2 = eigenvals
        
        # Check for real vs complex eigenvalues
        if np.isreal(lambda1) and np.isreal(lambda2):
            # Real eigenvalues
            lambda1, lambda2 = np.real(lambda1), np.real(lambda2)
            
            if lambda1 > 0 and lambda2 > 0:
                return "Nodo inestable (repulsor)"
            elif lambda1 < 0 and lambda2 < 0:
                return "Nodo estable (atractor)"
            elif (lambda1 > 0 and lambda2 < 0) or (lambda1 < 0 and lambda2 > 0):
                return "Punto silla (inestable)"
            elif lambda1 == 0 or lambda2 == 0:
                return "Caso degenerado (autovalor cero)"
            else:
                return "Caso no clasificado"
        else:
            # Complex eigenvalues
            real_part = np.real(lambda1)  # Both have same real part for 2x2 real matrices
            imag_part = np.imag(lambda1)
            
            if real_part > 0:
                return "Espiral inestable"
            elif real_part < 0:
                return "Espiral estable"
            elif real_part == 0:
                return "Centro (órbitas cerradas)"
            else:
                return "Caso no clasificado"

    def _update_results(self, A, eigenvals, eigenvecs, classification):
        """Update the results display with detailed step-by-step analysis."""
        self.txt_results.config(state='normal')
        self.txt_results.delete('1.0', tk.END)
        
        self.txt_results.insert(tk.END, "== ANÁLISIS PASO A PASO DEL SISTEMA LINEAL ==\n\n")
        
        # Step 1: System definition
        self.txt_results.insert(tk.END, "PASO 1: DEFINICIÓN DEL SISTEMA\n")
        self.txt_results.insert(tk.END, "=" * 35 + "\n")
        
        if self.input_mode.get() == "equations":
            self.txt_results.insert(tk.END, f"Sistema original:\n")
            self.txt_results.insert(tk.END, f"  x' = {self.x_prime_str.get()}\n")
            self.txt_results.insert(tk.END, f"  y' = {self.y_prime_str.get()}\n\n")
        
        self.txt_results.insert(tk.END, f"En forma matricial: x' = Ax, donde:\n")
        self.txt_results.insert(tk.END, f"A = ┌ {A[0,0]:6.2f}  {A[0,1]:6.2f} ┐\n")
        self.txt_results.insert(tk.END, f"    └ {A[1,0]:6.2f}  {A[1,1]:6.2f} ┘\n\n")
        
        # Step 2: Characteristic polynomial
        self.txt_results.insert(tk.END, "PASO 2: POLINOMIO CARACTERÍSTICO\n")
        self.txt_results.insert(tk.END, "=" * 35 + "\n")
        
        det_A = np.linalg.det(A)
        trace_A = np.trace(A)
        
        self.txt_results.insert(tk.END, f"Calculamos det(A - λI):\n")
        self.txt_results.insert(tk.END, f"A - λI = ┌ {A[0,0]:.2f} - λ    {A[0,1]:6.2f} ┐\n")
        self.txt_results.insert(tk.END, f"         └ {A[1,0]:6.2f}      {A[1,1]:.2f} - λ ┘\n\n")
        
        self.txt_results.insert(tk.END, f"det(A - λI) = ({A[0,0]:.2f} - λ)({A[1,1]:.2f} - λ) - ({A[0,1]:.2f})({A[1,0]:.2f})\n")
        self.txt_results.insert(tk.END, f"            = λ² - ({trace_A:.2f})λ + ({det_A:.2f})\n")
        self.txt_results.insert(tk.END, f"            = λ² - (traza)λ + (determinante)\n\n")
        
        self.txt_results.insert(tk.END, f"Traza(A) = {A[0,0]:.2f} + {A[1,1]:.2f} = {trace_A:.2f}\n")
        self.txt_results.insert(tk.END, f"Det(A) = ({A[0,0]:.2f})({A[1,1]:.2f}) - ({A[0,1]:.2f})({A[1,0]:.2f}) = {det_A:.2f}\n\n")
        
        # Step 3: Eigenvalues calculation
        self.txt_results.insert(tk.END, "PASO 3: CÁLCULO DE AUTOVALORES\n")
        self.txt_results.insert(tk.END, "=" * 35 + "\n")
        
        self.txt_results.insert(tk.END, f"Resolvemos: λ² - {trace_A:.2f}λ + {det_A:.2f} = 0\n")
        
        # Show quadratic formula
        discriminant = trace_A**2 - 4*det_A
        self.txt_results.insert(tk.END, f"Usando fórmula cuadrática:\n")
        self.txt_results.insert(tk.END, f"λ = (traza ± √(traza² - 4·det)) / 2\n")
        self.txt_results.insert(tk.END, f"λ = ({trace_A:.2f} ± √({trace_A:.2f}² - 4·{det_A:.2f})) / 2\n")
        self.txt_results.insert(tk.END, f"λ = ({trace_A:.2f} ± √{discriminant:.2f}) / 2\n\n")
        
        # Show eigenvalues
        self.txt_results.insert(tk.END, "Autovalores obtenidos:\n")
        for i, val in enumerate(eigenvals):
            if np.isreal(val):
                self.txt_results.insert(tk.END, f"λ{i+1} = {np.real(val):.2f}\n")
            else:
                real_part, imag_part = np.real(val), np.imag(val)
                sign = '+' if imag_part >= 0 else '-'
                self.txt_results.insert(tk.END, f"λ{i+1} = {real_part:.2f} {sign} {abs(imag_part):.2f}i\n")
        
        # Interpretation of eigenvalues
        self.txt_results.insert(tk.END, f"\nInterpretación del discriminante:\n")
        if discriminant > 0:
            self.txt_results.insert(tk.END, f"Δ = {discriminant:.2f} > 0 → Autovalores reales distintos\n")
        elif discriminant == 0:
            self.txt_results.insert(tk.END, f"Δ = {discriminant:.2f} = 0 → Autovalores reales iguales\n")
        else:
            self.txt_results.insert(tk.END, f"Δ = {discriminant:.2f} < 0 → Autovalores complejos conjugados\n")
        
        self.txt_results.insert(tk.END, "\n")
        
        # Step 4: Eigenvectors (only for real eigenvalues)
        if np.isreal(eigenvals[0]) and np.isreal(eigenvals[1]):
            self.txt_results.insert(tk.END, "PASO 4: CÁLCULO DE AUTOVECTORES\n")
            self.txt_results.insert(tk.END, "=" * 35 + "\n")
            
            for i, val in enumerate(eigenvals):
                lambda_val = np.real(val)
                self.txt_results.insert(tk.END, f"Para λ{i+1} = {lambda_val:.2f}:\n")
                self.txt_results.insert(tk.END, f"Resolvemos (A - λ{i+1}I)v = 0\n")
                
                # Calculate A - λI
                A_lambda = A - lambda_val * np.eye(2)
                self.txt_results.insert(tk.END, f"(A - {lambda_val:.2f}I) = ┌ {A_lambda[0,0]:8.2f}  {A_lambda[0,1]:8.2f} ┐\n")
                self.txt_results.insert(tk.END, f"                         └ {A_lambda[1,0]:8.2f}  {A_lambda[1,1]:8.2f} ┘\n")
                
                # Show eigenvector
                vec = eigenvecs[:, i]
                if np.isreal(vec[0]) and np.isreal(vec[1]):
                    v1, v2 = np.real(vec[0]), np.real(vec[1])
                    # Normalize to simpler form if possible
                    if abs(v1) > 1e-10:
                        ratio = v2/v1
                        self.txt_results.insert(tk.END, f"Autovector: v{i+1} = t·[1, {ratio:.2f}]ᵀ\n")
                        self.txt_results.insert(tk.END, f"Forma normalizada: v{i+1} = [{v1:8.2f}, {v2:8.2f}]ᵀ\n")
                    else:
                        self.txt_results.insert(tk.END, f"Autovector: v{i+1} = [{v1:8.2f}, {v2:8.2f}]ᵀ\n")
                self.txt_results.insert(tk.END, "\n")
        
        # Step 5: Classification
        self.txt_results.insert(tk.END, "PASO 5: CLASIFICACIÓN DEL PUNTO CRÍTICO\n")
        self.txt_results.insert(tk.END, "=" * 40 + "\n")
        
        self.txt_results.insert(tk.END, f"Criterios de clasificación:\n")
        self.txt_results.insert(tk.END, f"• Determinante = {det_A:.2f}\n")
        self.txt_results.insert(tk.END, f"• Traza = {trace_A:.2f}\n")
        self.txt_results.insert(tk.END, f"• Discriminante = {discriminant:.2f}\n\n")
        
        # Detailed classification logic
        if np.isreal(eigenvals[0]) and np.isreal(eigenvals[1]):
            lambda1, lambda2 = np.real(eigenvals[0]), np.real(eigenvals[1])
            self.txt_results.insert(tk.END, f"Autovalores reales: λ₁ = {lambda1:.2f}, λ₂ = {lambda2:.2f}\n")
            
            if lambda1 > 0 and lambda2 > 0:
                self.txt_results.insert(tk.END, f"Ambos autovalores positivos → NODO INESTABLE\n")
                self.txt_results.insert(tk.END, f"Las trayectorias se alejan del origen\n")
            elif lambda1 < 0 and lambda2 < 0:
                self.txt_results.insert(tk.END, f"Ambos autovalores negativos → NODO ESTABLE\n")
                self.txt_results.insert(tk.END, f"Las trayectorias convergen al origen\n")
            elif (lambda1 > 0 and lambda2 < 0) or (lambda1 < 0 and lambda2 > 0):
                self.txt_results.insert(tk.END, f"Autovalores de signo opuesto → PUNTO SILLA\n")
                self.txt_results.insert(tk.END, f"Existe variedad estable e inestable\n")
            elif lambda1 == 0 or lambda2 == 0:
                self.txt_results.insert(tk.END, f"Autovalor cero → CASO DEGENERADO\n")
        else:
            real_part = np.real(eigenvals[0])
            imag_part = np.imag(eigenvals[0])
            self.txt_results.insert(tk.END, f"Autovalores complejos: {real_part:.2f} ± {abs(imag_part):.2f}i\n")
            
            if real_part > 0:
                self.txt_results.insert(tk.END, f"Parte real positiva → ESPIRAL INESTABLE\n")
                self.txt_results.insert(tk.END, f"Las trayectorias espiralan alejándose del origen\n")
            elif real_part < 0:
                self.txt_results.insert(tk.END, f"Parte real negativa → ESPIRAL ESTABLE\n")
                self.txt_results.insert(tk.END, f"Las trayectorias espiralan hacia el origen\n")
            elif real_part == 0:
                self.txt_results.insert(tk.END, f"Parte real cero → CENTRO\n")
                self.txt_results.insert(tk.END, f"Las trayectorias son órbitas cerradas\n")
        
        self.txt_results.insert(tk.END, f"\nCLASIFICACIÓN FINAL: {classification}\n\n")
        
        # Step 6: Solution form
        self.txt_results.insert(tk.END, "PASO 6: FORMA GENERAL DE LA SOLUCIÓN\n")
        self.txt_results.insert(tk.END, "=" * 40 + "\n")
        
        if np.isreal(eigenvals[0]) and np.isreal(eigenvals[1]):
            lambda1, lambda2 = np.real(eigenvals[0]), np.real(eigenvals[1])
            v1, v2 = eigenvecs[:, 0], eigenvecs[:, 1]
            self.txt_results.insert(tk.END, f"Para autovalores reales:\n")
            self.txt_results.insert(tk.END, f"x(t) = c₁·e^({lambda1:.2f}t)·v₁ + c₂·e^({lambda2:.2f}t)·v₂\n")
            self.txt_results.insert(tk.END, f"donde c₁, c₂ son constantes determinadas por condiciones iniciales\n")
        else:
            real_part = np.real(eigenvals[0])
            imag_part = np.imag(eigenvals[0])
            self.txt_results.insert(tk.END, f"Para autovalores complejos:\n")
            self.txt_results.insert(tk.END, f"x(t) = e^({real_part:.2f}t)[c₁·cos({abs(imag_part):.2f}t)·u + c₂·sen({abs(imag_part):.2f}t)·v]\n")
            self.txt_results.insert(tk.END, f"donde u, v son las partes real e imaginaria del autovector\n")
        
        self.txt_results.config(state='disabled')

    def _plot_phase_portrait(self, A):
        """Plot the phase portrait with vector field and eigenspaces."""
        self.ax_phase.clear()
        
        # Get plot bounds
        x_min, x_max = self.x_min.get(), self.x_max.get()
        y_min, y_max = self.y_min.get(), self.y_max.get()
        
        # Create grid for vector field
        x = np.linspace(x_min, x_max, 20)
        y = np.linspace(y_min, y_max, 20)
        X, Y = np.meshgrid(x, y)
        
        # Calculate vector field
        DX = A[0,0] * X + A[0,1] * Y
        DY = A[1,0] * X + A[1,1] * Y
        
        # Normalize vectors for better visualization
        M = np.sqrt(DX**2 + DY**2)
        M[M == 0] = 1  # Avoid division by zero
        DX_norm = DX / M
        DY_norm = DY / M
        
        # Plot vector field with improved arrow orientation
        self.ax_phase.quiver(X, Y, DX_norm, DY_norm, M, 
                           cmap='viridis', alpha=0.6, 
                           scale=25, scale_units='xy',
                           width=0.004, headwidth=4, headlength=5,
                           pivot='mid')  # Center arrows on grid points
        
        # Plot eigenspaces for real eigenvalues
        if np.isreal(self._current_eigenvalues[0]) and np.isreal(self._current_eigenvalues[1]):
            eigenvals = np.real(self._current_eigenvalues)
            eigenvecs = np.real(self._current_eigenvectors)
            
            # Plot eigenvector directions
            for i, (val, vec) in enumerate(zip(eigenvals, eigenvecs.T)):
                if abs(vec[1]) > 1e-10:  # Avoid vertical lines
                    slope = vec[1] / vec[0]
                    x_line = np.linspace(x_min, x_max, 100)
                    y_line = slope * x_line
                    
                    # Filter points within bounds
                    mask = (y_line >= y_min) & (y_line <= y_max)
                    
                    color = 'red' if val > 0 else 'blue'
                    linestyle = '-' if val > 0 else '--'
                    label = f'Autovector {i+1} (λ={val:.2f})'
                    
                    self.ax_phase.plot(x_line[mask], y_line[mask], color=color, 
                                     linestyle=linestyle, linewidth=2, label=label)
                else:
                    # Vertical eigenvector
                    self.ax_phase.axvline(x=0, color='red' if val > 0 else 'blue',
                                        linestyle='-' if val > 0 else '--', linewidth=2,
                                        label=f'Autovector {i+1} (λ={val:.2f})')
        
        # Plot some sample trajectories
        self._plot_sample_trajectories(A)
        
        # Formatting
        self.ax_phase.set_xlim(x_min, x_max)
        self.ax_phase.set_ylim(y_min, y_max)
        self.ax_phase.set_xlabel('x')
        self.ax_phase.set_ylabel('y')
        self.ax_phase.set_title(f'Retrato de Fase - {self._current_classification}')
        self.ax_phase.grid(True, alpha=0.3)
        self.ax_phase.axhline(y=0, color='k', linewidth=0.5)
        self.ax_phase.axvline(x=0, color='k', linewidth=0.5)
        self.ax_phase.legend()
        
        # Bind click event for interactive trajectories
        if self.click_cid:
            self.canvas_phase.mpl_disconnect(self.click_cid)
        self.click_cid = self.canvas_phase.mpl_connect('button_press_event', 
                                                       lambda event: self._on_phase_click(event, A))
        
        self.canvas_phase.draw()

    def _plot_poincare_map(self, A):
        """Plot Poincaré map showing discrete-time sampling of trajectories."""
        self.ax_poincare.clear()
        
        x_min, x_max = self.x_min.get(), self.x_max.get()
        y_min, y_max = self.y_min.get(), self.y_max.get()
        t_max = self.time_max.get()
        dt = self.poincare_dt.get()
        
        # Generate initial conditions (same as sample trajectories)
        initial_conditions = [
            (x_max * 0.8, 0), (-x_max * 0.8, 0),
            (0, y_max * 0.8), (0, -y_max * 0.8),
            (x_max * 0.6, y_max * 0.6), (-x_max * 0.6, -y_max * 0.6),
            (x_max * 0.6, -y_max * 0.6), (-x_max * 0.6, y_max * 0.6)
        ]
        
        # Create discrete time samples
        t_samples = np.arange(0, t_max, dt)
        
        # Check if using forcing functions
        use_forcing = self.use_forcing.get()
        if use_forcing:
            # Parse forcing functions
            try:
                import sympy as sp
                t_sym = sp.Symbol('t')
                f1_expr = sp.sympify(self.f1_str.get())
                f2_expr = sp.sympify(self.f2_str.get())
                f1_func = sp.lambdify(t_sym, f1_expr, 'numpy')
                f2_func = sp.lambdify(t_sym, f2_expr, 'numpy')
            except:
                messagebox.showerror("Error", "Error al parsear funciones de forzamiento")
                return
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(initial_conditions)))
        
        for idx, (x0, y0) in enumerate(initial_conditions):
            # Skip if initial condition is at origin
            if abs(x0) < 1e-10 and abs(y0) < 1e-10:
                continue
            
            # Solve the system for discrete time points
            try:
                eigenvals, eigenvecs = self._current_eigenvalues, self._current_eigenvectors
                
                x_points = []
                y_points = []
                
                if use_forcing:
                    # Solve non-homogeneous system for all time samples at once
                    solution = self._solve_nonhomogeneous(A, np.array([x0, y0]), t_samples, f1_func, f2_func)
                    for i in range(len(t_samples)):
                        x_t, y_t = solution[i, 0], solution[i, 1]
                        if x_min <= x_t <= x_max and y_min <= y_t <= y_max:
                            x_points.append(x_t)
                            y_points.append(y_t)
                else:
                    # Homogeneous system
                    for t in t_samples:
                        if np.isreal(eigenvals[0]) and np.isreal(eigenvals[1]):
                            # Real eigenvalues case
                            solution = self._solve_real_eigenvalues(A, np.array([x0, y0]), np.array([t]))
                        else:
                            # Complex eigenvalues case
                            solution = self._solve_complex_eigenvalues(A, np.array([x0, y0]), np.array([t]))
                        
                        x_t = solution[0, 0]
                        y_t = solution[1, 0]
                        
                        # Check if point is within bounds
                        if x_min <= x_t <= x_max and y_min <= y_t <= y_max:
                            x_points.append(x_t)
                            y_points.append(y_t)
                
                # Plot discrete points
                if x_points:
                    self.ax_poincare.scatter(x_points, y_points, c=[colors[idx]], 
                                            s=30, alpha=0.7, edgecolors='black', linewidth=0.5,
                                            label=f'CI: ({x0:.1f}, {y0:.1f})')
                    
                    # Connect points with thin lines to show evolution
                    self.ax_poincare.plot(x_points, y_points, c=colors[idx], 
                                         alpha=0.2, linewidth=0.5, linestyle=':')
                    
            except Exception as e:
                continue
        
        # Plot eigenvector directions if real
        if np.isreal(self._current_eigenvalues[0]) and np.isreal(self._current_eigenvalues[1]):
            eigenvals = np.real(self._current_eigenvalues)
            eigenvecs = np.real(self._current_eigenvectors)
            
            for i, (val, vec) in enumerate(zip(eigenvals, eigenvecs.T)):
                if abs(vec[1]) > 1e-10:
                    slope = vec[1] / vec[0]
                    x_line = np.linspace(x_min, x_max, 100)
                    y_line = slope * x_line
                    mask = (y_line >= y_min) & (y_line <= y_max)
                    
                    color = 'red' if val > 0 else 'blue'
                    linestyle = '--'
                    self.ax_poincare.plot(x_line[mask], y_line[mask], color=color,
                                         linestyle=linestyle, linewidth=1, alpha=0.4)
                else:
                    color = 'red' if val > 0 else 'blue'
                    self.ax_poincare.axvline(x=0, color=color, linestyle='--', 
                                           linewidth=1, alpha=0.4)
        
        # Formatting
        self.ax_poincare.set_xlim(x_min, x_max)
        self.ax_poincare.set_ylim(y_min, y_max)
        self.ax_poincare.set_xlabel('x')
        self.ax_poincare.set_ylabel('y')
        
        # Title depends on whether forcing is used
        title_suffix = " (con forzamiento)" if use_forcing else ""
        self.ax_poincare.set_title(f'Mapa de Poincaré (Δt = {dt}){title_suffix} - {self._current_classification}')
        self.ax_poincare.grid(True, alpha=0.3)
        self.ax_poincare.axhline(y=0, color='k', linewidth=0.5)
        self.ax_poincare.axvline(x=0, color='k', linewidth=0.5)
        self.ax_poincare.legend(fontsize=8, loc='best')
        
        self.canvas_poincare.draw()

    def _plot_sample_trajectories(self, A):
        """Plot sample solution trajectories."""
        x_min, x_max = self.x_min.get(), self.x_max.get()
        y_min, y_max = self.y_min.get(), self.y_max.get()
        t_max = self.time_max.get()
        
        # Generate initial conditions
        initial_conditions = [
            (x_max * 0.8, 0), (-x_max * 0.8, 0),
            (0, y_max * 0.8), (0, -y_max * 0.8),
            (x_max * 0.6, y_max * 0.6), (-x_max * 0.6, -y_max * 0.6),
            (x_max * 0.6, -y_max * 0.6), (-x_max * 0.6, y_max * 0.6)
        ]
        
        t = np.linspace(0, t_max, 1000)
        
        for x0, y0 in initial_conditions:
            # Skip if initial condition is at origin
            if abs(x0) < 1e-10 and abs(y0) < 1e-10:
                continue
                
            # Solve the system analytically
            try:
                # For 2D linear system x' = Ax, solution is x(t) = exp(At) * x0
                eigenvals, eigenvecs = self._current_eigenvalues, self._current_eigenvectors
                
                if np.isreal(eigenvals[0]) and np.isreal(eigenvals[1]):
                    # Real eigenvalues case
                    solution = self._solve_real_eigenvalues(A, np.array([x0, y0]), t)
                else:
                    # Complex eigenvalues case
                    solution = self._solve_complex_eigenvalues(A, np.array([x0, y0]), t)
                
                # Extract x and y components
                x_traj = solution[:, 0]
                y_traj = solution[:, 1]
                
                # Plot trajectory
                self.ax_phase.plot(x_traj, y_traj, 'g-', alpha=0.7, linewidth=1)
                self.ax_phase.plot(x0, y0, 'ro', markersize=4)  # Initial condition
                
            except Exception as e:
                print(f"Error plotting trajectory from ({x0}, {y0}): {e}")
                continue

    def _solve_real_eigenvalues(self, A, x0, t):
        """Solve system with real eigenvalues."""
        eigenvals, eigenvecs = np.linalg.eig(A)
        eigenvals = np.real(eigenvals)
        eigenvecs = np.real(eigenvecs)
        
        # Express initial condition in eigenvector basis
        try:
            coeffs = np.linalg.solve(eigenvecs, x0)
        except np.linalg.LinAlgError:
            # Fallback to matrix exponential
            return self._solve_matrix_exponential(A, x0, t)
        
        # Construct solution
        solution = np.zeros((len(t), 2))
        for i, time in enumerate(t):
            exp_lambda_t = np.exp(eigenvals * time)
            x_t = eigenvecs @ (coeffs * exp_lambda_t)
            solution[i] = x_t
            
        return solution

    def _solve_complex_eigenvalues(self, A, x0, t):
        """Solve system with complex eigenvalues."""
        return self._solve_matrix_exponential(A, x0, t)

    def _solve_matrix_exponential(self, A, x0, t):
        """Solve using matrix exponential (general method)."""
        from scipy.linalg import expm
        
        solution = np.zeros((len(t), 2))
        for i, time in enumerate(t):
            solution[i] = expm(A * time) @ x0
            
        return solution

    def _solve_nonhomogeneous(self, A, x0, t, f1_func, f2_func):
        """
        Solve non-homogeneous system: x' = Ax + f(t)
        Using variation of parameters / integrating factor method.
        Solution: x(t) = exp(At)x₀ + ∫₀ᵗ exp(A(t-s))f(s) ds
        """
        from scipy.linalg import expm
        from scipy.integrate import odeint
        
        # Define the ODE system
        def system(state, time):
            x, y = state
            f1 = f1_func(time)
            f2 = f2_func(time)
            dx = A[0,0]*x + A[0,1]*y + f1
            dy = A[1,0]*x + A[1,1]*y + f2
            return [dx, dy]
        
        # Solve using numerical integration
        solution = odeint(system, x0, t)
        return solution

    def _plot_solution_trajectories(self, A):
        """Plot x(t) and y(t) vs time for selected initial conditions."""
        self.ax_traj.clear()
        
        t_max = self.time_max.get()
        t = np.linspace(0, t_max, 1000)
        
        # Plot for a few selected initial conditions
        initial_conditions = [
            (1, 0, 'blue', 'x₀=(1,0)'),
            (0, 1, 'red', 'x₀=(0,1)'),
            (1, 1, 'green', 'x₀=(1,1)')
        ]
        
        for x0, y0, color, label in initial_conditions:
            try:
                if np.isreal(self._current_eigenvalues[0]) and np.isreal(self._current_eigenvalues[1]):
                    solution = self._solve_real_eigenvalues(A, np.array([x0, y0]), t)
                else:
                    solution = self._solve_complex_eigenvalues(A, np.array([x0, y0]), t)
                
                x_traj = solution[:, 0]
                y_traj = solution[:, 1]
                
                self.ax_traj.plot(t, x_traj, color=color, linestyle='-', 
                                label=f'x(t), {label}', linewidth=1.5)
                self.ax_traj.plot(t, y_traj, color=color, linestyle='--', 
                                label=f'y(t), {label}', linewidth=1.5)
                
            except Exception as e:
                print(f"Error plotting trajectory for {label}: {e}")
                continue
        
        self.ax_traj.set_xlabel('Tiempo t')
        self.ax_traj.set_ylabel('x(t), y(t)')
        self.ax_traj.set_title('Evolución Temporal de las Soluciones')
        self.ax_traj.grid(True, alpha=0.3)
        self.ax_traj.legend()
        self.ax_traj.axhline(y=0, color='k', linewidth=0.5)
        
        self.canvas_traj.draw()

    def _on_phase_click(self, event, A):
        """Handle click event to plot trajectory from clicked point on phase portrait."""
        # Validate click is in the axes
        if event.inaxes != self.ax_phase:
            return
        
        # Get coordinates
        x0, y0 = event.xdata, event.ydata
        
        # Validate coordinates
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
            self._plot_single_trajectory(A, x0, y0, color='red', alpha=0.9, linewidth=2)
            
            # Redraw canvas
            self.canvas_phase.draw_idle()
        except Exception as e:
            print(f"Error plotting trajectory: {e}")
            # Remove the failed trajectory from list
            if self.clicked_trajectories and self.clicked_trajectories[-1] == (x0, y0):
                self.clicked_trajectories.pop()
    
    def _plot_single_trajectory(self, A, x0, y0, color='blue', alpha=0.8, linewidth=1.5):
        """Plot a single trajectory from initial condition (x0, y0)."""
        t_max = self.time_max.get()
        direction = self.trajectory_direction.get()
        
        # Check if using forcing functions
        use_forcing = self.use_forcing.get()
        
        if use_forcing:
            # Use non-homogeneous system
            try:
                t_sym = sp.Symbol('t')
                f1_expr = sp.sympify(self.f1_str.get())
                f2_expr = sp.sympify(self.f2_str.get())
                f1_func = sp.lambdify(t_sym, f1_expr, 'numpy')
                f2_func = sp.lambdify(t_sym, f2_expr, 'numpy')
                
                def system_func(state, t):
                    x, y = state
                    f1_val = f1_func(t)
                    f2_val = f2_func(t)
                    if not np.isfinite(f1_val):
                        f1_val = 0
                    if not np.isfinite(f2_val):
                        f2_val = 0
                    dx = A[0,0] * x + A[0,1] * y + f1_val
                    dy = A[1,0] * x + A[1,1] * y + f2_val
                    return [dx, dy]
            except:
                # Fall back to homogeneous
                def system_func(state, t):
                    x, y = state
                    dx = A[0,0] * x + A[0,1] * y
                    dy = A[1,0] * x + A[1,1] * y
                    return [dx, dy]
        else:
            # Homogeneous system
            def system_func(state, t):
                x, y = state
                dx = A[0,0] * x + A[0,1] * y
                dy = A[1,0] * x + A[1,1] * y
                return [dx, dy]
        
        # Forward integration
        if direction in ["forward", "both"]:
            t_forward = np.linspace(0, t_max, 200)
            try:
                from scipy.integrate import odeint
                sol_forward = odeint(system_func, [x0, y0], t_forward)
                
                if len(sol_forward) > 1:
                    valid_mask = np.isfinite(sol_forward[:, 0]) & np.isfinite(sol_forward[:, 1])
                    if np.any(valid_mask):
                        sol_valid = sol_forward[valid_mask]
                        if len(sol_valid) > 1:
                            self.ax_phase.plot(sol_valid[:, 0], sol_valid[:, 1], color=color, 
                                             alpha=alpha, linewidth=linewidth, zorder=3)
            except:
                pass
        
        # Backward integration
        if direction in ["backward", "both"]:
            t_backward = np.linspace(0, -t_max, 200)
            try:
                from scipy.integrate import odeint
                sol_backward = odeint(system_func, [x0, y0], t_backward)
                
                if len(sol_backward) > 1:
                    valid_mask = np.isfinite(sol_backward[:, 0]) & np.isfinite(sol_backward[:, 1])
                    if np.any(valid_mask):
                        sol_valid = sol_backward[valid_mask]
                        if len(sol_valid) > 1:
                            self.ax_phase.plot(sol_valid[:, 0], sol_valid[:, 1], color=color, 
                                             alpha=alpha, linewidth=linewidth, linestyle='--', zorder=3)
            except:
                pass
        
        # Mark initial point
        try:
            self.ax_phase.plot(x0, y0, 'o', color=color, markersize=6, 
                             markeredgecolor='black', markeredgewidth=0.5, zorder=4)
        except:
            pass
    
    def clear_clicked_trajectories(self):
        """Clear clicked trajectories and replot."""
        self.clicked_trajectories = []
        if self._current_matrix is not None:
            try:
                # Replot phase portrait without clicked trajectories
                self._plot_phase_portrait(self._current_matrix)
            except Exception as e:
                print(f"Error reploting: {e}")
    
    def clear_plots(self):
        """Clear all plots."""
        self.clicked_trajectories = []
        if self.click_cid:
            try:
                self.canvas_phase.mpl_disconnect(self.click_cid)
                self.click_cid = None
            except:
                pass
        
        self.ax_phase.clear()
        self.ax_phase.set_title('Retrato de Fase')
        self.ax_phase.set_xlabel('x')
        self.ax_phase.set_ylabel('y')
        self.canvas_phase.draw()
        
        self.ax_poincare.clear()
        self.ax_poincare.set_title('Mapa de Poincaré')
        self.ax_poincare.set_xlabel('x')
        self.ax_poincare.set_ylabel('y')
        self.canvas_poincare.draw()
        
        self.ax_traj.clear()
        self.ax_traj.set_title('Trayectorias de Solución')
        self.ax_traj.set_xlabel('Tiempo t')
        self.ax_traj.set_ylabel('x(t), y(t)')
        self.canvas_traj.draw()
        
        self._write_results_header()
        self.status.set("Gráficos limpiados.")

if __name__ == "__main__":
    app = LinearSystem2DApp()
    app.mainloop()