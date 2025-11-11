#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistemas Dinámicos Lineales 2D - VERSIÓN SIMPLIFICADA Y CORREGIDA
Sistema: x' = Ax donde A es una matriz 2x2
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.integrate import odeint

class LinearSystem2DApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistemas Dinámicos Lineales 2D - Análisis Completo")
        self.geometry("1500x900")
        
        # Theme colors
        self.theme_color = "#3498db"
        self.theme_color_light = "#5dade2"
        
        # Matrix coefficients: x' = a11*x + a12*y, y' = a21*x + a22*y
        self.a11 = tk.DoubleVar(value=1.0)
        self.a12 = tk.DoubleVar(value=0.0)
        self.a21 = tk.DoubleVar(value=0.0)
        self.a22 = tk.DoubleVar(value=-1.0)
        
        # Plot parameters
        self.x_min = tk.DoubleVar(value=-3.0)
        self.x_max = tk.DoubleVar(value=3.0)
        self.y_min = tk.DoubleVar(value=-3.0)
        self.y_max = tk.DoubleVar(value=3.0)
        self.time_max = tk.DoubleVar(value=5.0)
        
        # Quick examples
        self.examples = {
            "Nodo estable": {"a11": -1, "a12": 0, "a21": 0, "a22": -1},
            "Nodo inestable": {"a11": 1, "a12": 0, "a21": 0, "a22": 1},
            "Silla de montar": {"a11": 1, "a12": 0, "a21": 0, "a22": -1},
            "Centro (órbitas)": {"a11": 0, "a12": -1, "a21": 1, "a22": 0},
            "Espiral estable": {"a11": -1, "a12": -1, "a21": 1, "a22": -1},
            "Espiral inestable": {"a11": 1, "a12": -1, "a21": 1, "a22": 1},
        }
        
        self._create_ui()
        
    def _create_ui(self):
        """Create the user interface."""
        # Main container
        main_container = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel
        left_panel = ttk.Frame(main_container, width=400)
        main_container.add(left_panel, weight=0)
        
        # Right panel
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=1)
        
        self._create_left_panel(left_panel)
        self._create_right_panel(right_panel)
        
    def _create_left_panel(self, parent):
        """Create control panel."""
        # Title
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(title_frame, text="Sistemas Lineales 2D", 
                 font=("Arial", 14, "bold")).pack()
        ttk.Label(title_frame, text="x' = Ax", 
                 font=("Arial", 10, "italic")).pack()
        
        # Quick examples
        examples_frame = ttk.LabelFrame(parent, text="Ejemplos Rápidos")
        examples_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for i, (name, _) in enumerate(self.examples.items()):
            row = i // 2
            col = i % 2
            btn = tk.Button(examples_frame, text=name,
                          command=lambda n=name: self._load_example(n),
                          bg=self.theme_color, fg='white',
                          activebackground=self.theme_color_light,
                          font=("Arial", 9, "bold"),
                          cursor='hand2', relief=tk.RAISED, bd=2)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        examples_frame.grid_columnconfigure(0, weight=1)
        examples_frame.grid_columnconfigure(1, weight=1)
        
        # Matrix input
        matrix_frame = ttk.LabelFrame(parent, text="Matriz del Sistema")
        matrix_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(matrix_frame, text="x' = a11·x + a12·y", 
                 font=("Arial", 9, "italic")).pack(anchor='w', padx=5)
        ttk.Label(matrix_frame, text="y' = a21·x + a22·y", 
                 font=("Arial", 9, "italic")).pack(anchor='w', padx=5)
        
        # Matrix A = [[a11, a12], [a21, a22]]
        matrix_grid = ttk.Frame(matrix_frame)
        matrix_grid.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(matrix_grid, text="A =").grid(row=0, column=0, padx=5)
        ttk.Label(matrix_grid, text="[").grid(row=0, column=1)
        ttk.Entry(matrix_grid, textvariable=self.a11, width=8).grid(row=0, column=2)
        ttk.Entry(matrix_grid, textvariable=self.a12, width=8).grid(row=0, column=3)
        ttk.Label(matrix_grid, text="]").grid(row=0, column=4)
        
        ttk.Label(matrix_grid, text="[").grid(row=1, column=1)
        ttk.Entry(matrix_grid, textvariable=self.a21, width=8).grid(row=1, column=2)
        ttk.Entry(matrix_grid, textvariable=self.a22, width=8).grid(row=1, column=3)
        ttk.Label(matrix_grid, text="]").grid(row=1, column=4)
        
        # Plot controls
        plot_frame = ttk.LabelFrame(parent, text="Controles del Gráfico")
        plot_frame.pack(fill=tk.X, padx=10, pady=5)
        
        controls = [
            ("x min:", self.x_min), ("x max:", self.x_max),
            ("y min:", self.y_min), ("y max:", self.y_max),
            ("tiempo max:", self.time_max)
        ]
        
        for i, (label, var) in enumerate(controls):
            frame = ttk.Frame(plot_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(frame, text=label, width=12).pack(side=tk.LEFT)
            ttk.Entry(frame, textvariable=var, width=10).pack(side=tk.LEFT)
        
        # Action buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(btn_frame, text="🔍 Analizar Sistema",
                 command=self.analyze_system,
                 bg=self.theme_color, fg='white',
                 activebackground=self.theme_color_light,
                 font=("Arial", 11, "bold"),
                 cursor='hand2', relief=tk.RAISED, bd=2).pack(fill=tk.X, pady=5)
        
        tk.Button(btn_frame, text="🧹 Limpiar",
                 command=self.clear_all,
                 bg=self.theme_color, fg='white',
                 activebackground=self.theme_color_light,
                 font=("Arial", 11, "bold"),
                 cursor='hand2', relief=tk.RAISED, bd=2).pack(fill=tk.X, pady=5)
        
        # Info display
        info_frame = ttk.LabelFrame(parent, text="Información del Sistema")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.info_text = ScrolledText(info_frame, wrap='word', 
                                     font=("Consolas", 9), height=15)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def _create_right_panel(self, parent):
        """Create plot panel."""
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Connect click event
        self.canvas.mpl_connect('button_press_event', self._on_canvas_click)
        
    def _load_example(self, name):
        """Load a predefined example."""
        if name in self.examples:
            ex = self.examples[name]
            self.a11.set(ex["a11"])
            self.a12.set(ex["a12"])
            self.a21.set(ex["a21"])
            self.a22.set(ex["a22"])
            self.analyze_system()
        
    def analyze_system(self):
        """Analyze the linear system."""
        try:
            # Get matrix A
            A = np.array([
                [self.a11.get(), self.a12.get()],
                [self.a21.get(), self.a22.get()]
            ])
            
            # Calculate eigenvalues and eigenvectors
            eigenvalues, eigenvectors = np.linalg.eig(A)
            
            # Classify the system
            classification = self._classify_system(eigenvalues)
            
            # Update info text
            self._display_info(A, eigenvalues, eigenvectors, classification)
            
            # Plot phase portrait
            self._plot_phase_portrait(A, eigenvalues, eigenvectors, classification)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al analizar el sistema:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def _classify_system(self, eigenvalues):
        """Classify the system based on eigenvalues."""
        λ1, λ2 = eigenvalues
        
        # Check if eigenvalues are real or complex
        if np.isreal(λ1) and np.isreal(λ2):
            λ1_real = np.real(λ1)
            λ2_real = np.real(λ2)
            
            if λ1_real > 0 and λ2_real > 0:
                return "Nodo inestable (repulsor)"
            elif λ1_real < 0 and λ2_real < 0:
                return "Nodo estable (atractor)"
            elif λ1_real * λ2_real < 0:
                return "Silla de montar (punto silla)"
            else:  # One zero eigenvalue
                return "Línea de puntos críticos"
        else:
            # Complex eigenvalues: λ = α ± βi
            alpha = np.real(λ1)
            
            if abs(alpha) < 1e-10:
                return "Centro (órbitas cerradas)"
            elif alpha < 0:
                return "Espiral estable (foco atractor)"
            else:
                return "Espiral inestable (foco repulsor)"
    
    def _display_info(self, A, eigenvalues, eigenvectors, classification):
        """Display system information."""
        self.info_text.delete(1.0, tk.END)
        
        text = "═" * 50 + "\n"
        text += "ANÁLISIS DEL SISTEMA LINEAL 2D\n"
        text += "═" * 50 + "\n\n"
        
        text += "Sistema: x' = Ax\n\n"
        text += f"Matriz A:\n"
        text += f"  [{A[0,0]:7.3f}  {A[0,1]:7.3f}]\n"
        text += f"  [{A[1,0]:7.3f}  {A[1,1]:7.3f}]\n\n"
        
        text += "─" * 50 + "\n"
        text += f"CLASIFICACIÓN: {classification}\n"
        text += "─" * 50 + "\n\n"
        
        text += "Autovalores (eigenvalues):\n"
        for i, λ in enumerate(eigenvalues):
            if np.isreal(λ):
                text += f"  λ{i+1} = {np.real(λ):.6f}\n"
            else:
                text += f"  λ{i+1} = {np.real(λ):.6f} + {np.imag(λ):.6f}i\n"
        
        text += "\nAutovectores (eigenvectors):\n"
        for i in range(2):
            v = eigenvectors[:, i]
            if np.isreal(v[0]) and np.isreal(v[1]):
                text += f"  v{i+1} = [{np.real(v[0]):.6f}, {np.real(v[1]):.6f}]\n"
            else:
                text += f"  v{i+1} = [{v[0]:.6f}, {v[1]:.6f}]\n"
        
        # Additional properties
        det_A = np.linalg.det(A)
        trace_A = np.trace(A)
        
        text += "\n" + "─" * 50 + "\n"
        text += "Propiedades:\n"
        text += f"  Determinante: {det_A:.6f}\n"
        text += f"  Traza: {trace_A:.6f}\n"
        text += f"  Producto λ1·λ2 = {eigenvalues[0]*eigenvalues[1]:.6f}\n"
        text += f"  Suma λ1+λ2 = {eigenvalues[0]+eigenvalues[1]:.6f}\n"
        
        text += "\n" + "─" * 50 + "\n"
        text += "💡 Haz clic en el gráfico para ver trayectorias\n"
        
        self.info_text.insert(tk.END, text)
    
    def _plot_phase_portrait(self, A, eigenvalues, eigenvectors, classification):
        """Plot the phase portrait."""
        self.fig.clear()
        
        # Create single plot
        ax = self.fig.add_subplot(111)
        
        # Get bounds
        x_min, x_max = self.x_min.get(), self.x_max.get()
        y_min, y_max = self.y_min.get(), self.y_max.get()
        
        # Create vector field
        x = np.linspace(x_min, x_max, 20)
        y = np.linspace(y_min, y_max, 20)
        X, Y = np.meshgrid(x, y)
        
        # Calculate derivatives
        DX = A[0,0] * X + A[0,1] * Y
        DY = A[1,0] * X + A[1,1] * Y
        
        # Normalize for better visualization
        M = np.sqrt(DX**2 + DY**2)
        M[M == 0] = 1
        DX_norm = DX / M
        DY_norm = DY / M
        
        # Plot vector field
        ax.quiver(X, Y, DX_norm, DY_norm, M, 
                 cmap='viridis', alpha=0.6,
                 scale=25, width=0.004)
        
        # Plot eigenvectors if real
        if np.isreal(eigenvalues[0]) and np.isreal(eigenvalues[1]):
            for i, (λ, v) in enumerate(zip(eigenvalues, eigenvectors.T)):
                λ_real = np.real(λ)
                v_real = np.real(v)
                
                if abs(v_real[0]) > 1e-10:
                    slope = v_real[1] / v_real[0]
                    x_line = np.linspace(x_min, x_max, 100)
                    y_line = slope * x_line
                    
                    mask = (y_line >= y_min) & (y_line <= y_max)
                    
                    color = 'red' if λ_real > 0 else 'blue'
                    linestyle = '-' if λ_real > 0 else '--'
                    ax.plot(x_line[mask], y_line[mask], 
                           color=color, linestyle=linestyle, linewidth=2,
                           label=f'λ{i+1}={λ_real:.2f}')
        
        # Plot sample trajectories
        self._plot_trajectories(ax, A)
        
        # Formatting
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_xlabel('x', fontsize=12, fontweight='bold')
        ax.set_ylabel('y', fontsize=12, fontweight='bold')
        ax.set_title(f'Retrato de Fase - {classification}', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='k', linewidth=0.5)
        ax.axvline(x=0, color='k', linewidth=0.5)
        ax.legend(loc='best', fontsize=9)
        
        self.fig.tight_layout()
        self.canvas.draw()
        
        # Store current A for click events
        self.current_A = A
    
    def _plot_trajectories(self, ax, A):
        """Plot sample trajectories."""
        x_max = self.x_max.get()
        y_max = self.y_max.get()
        t_max = self.time_max.get()
        
        # Initial conditions
        initial_conditions = [
            (x_max * 0.8, 0), (-x_max * 0.8, 0),
            (0, y_max * 0.8), (0, -y_max * 0.8),
            (x_max * 0.6, y_max * 0.6), (-x_max * 0.6, -y_max * 0.6),
            (x_max * 0.6, -y_max * 0.6), (-x_max * 0.6, y_max * 0.6)
        ]
        
        t = np.linspace(0, t_max, 500)
        
        for x0, y0 in initial_conditions:
            if abs(x0) < 1e-10 and abs(y0) < 1e-10:
                continue
            
            try:
                # Solve ODE
                def system(state, t):
                    x, y = state
                    dx = A[0,0]*x + A[0,1]*y
                    dy = A[1,0]*x + A[1,1]*y
                    return [dx, dy]
                
                sol = odeint(system, [x0, y0], t)
                
                ax.plot(sol[:, 0], sol[:, 1], 'g-', alpha=0.5, linewidth=1)
                ax.plot(x0, y0, 'ro', markersize=4)
                
            except:
                continue
    
    def _on_canvas_click(self, event):
        """Handle canvas click to plot trajectory."""
        if event.inaxes and hasattr(self, 'current_A'):
            x0, y0 = event.xdata, event.ydata
            
            # Get the axis
            ax = self.fig.axes[0]
            
            # Solve and plot trajectory
            t_max = self.time_max.get()
            t = np.linspace(0, t_max, 500)
            
            def system(state, t):
                x, y = state
                A = self.current_A
                dx = A[0,0]*x + A[0,1]*y
                dy = A[1,0]*x + A[1,1]*y
                return [dx, dy]
            
            try:
                sol = odeint(system, [x0, y0], t)
                ax.plot(sol[:, 0], sol[:, 1], 'orange', linewidth=2, alpha=0.8)
                ax.plot(x0, y0, 'o', color='orange', markersize=8)
                self.canvas.draw()
            except:
                pass
    
    def clear_all(self):
        """Clear all plots and reset."""
        self.fig.clear()
        self.canvas.draw()
        self.info_text.delete(1.0, tk.END)
        if hasattr(self, 'current_A'):
            delattr(self, 'current_A')


if __name__ == "__main__":
    app = LinearSystem2DApp()
    app.mainloop()
