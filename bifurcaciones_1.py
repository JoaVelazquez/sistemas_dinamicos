#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#*******EDICION DE GRUPO 01******
#Se refactorizo el codigo eliminando repeticiones y metodos no utilizados - podria mejorarse utilizando principios SOLID
#Se elimino el problema de superposicion de puntos importantes en graficos, eliminando la funcion plot_important_points y agregando la funcionalidad a _create_phase_plot
#Tambien se volvio a incluir los graficos de fase debajo del grafico de bifurcacion para mayor comodidad del usuario
#Se agrego la funcionalidad de mostrar los resultados inmediatos en la misma pestaña sin necesidad de cambiar
#Se agrego la detección automática de tipos de bifurcación
#*********************************
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import numpy as np
import sympy as sp
from sympy import sympify, diff
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib as mpl

mpl.rcParams.update({
    "figure.dpi": 100,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "legend.fontsize": 10,
})

# ----------------- funciones auxiliares (sin cambios) -----------------

def unique_sorted(vals, tol=1e-5):
    vals = sorted(vals)
    out = []
    for v in vals:
        if not out or abs(v - out[-1]) > tol:
            out.append(v)
    return out

def poly_roots_real(f_expr, x_sym, r_sym, r_val):
    """Si f es polinómica en x, devuelve raíces reales evaluando coeficientes en r=r_val."""
    try:
        poly = sp.Poly(f_expr, x_sym)
    except Exception:
        return None  # no polinómica en x
    if not poly.is_univariate:
        return None
    coeffs = [sp.N(c.subs({r_sym: r_val})) for c in poly.all_coeffs()]
    # convertir a floats (si todavía hay símbolos, abortar)
    try:
        coeffs = [complex(c) for c in coeffs]
    except Exception:
        return None
    if np.allclose([c.real for c in coeffs], 0):
        return None
    roots = np.roots([c.real for c in coeffs])  # nos quedamos con parte real
    real_roots = [float(r.real) for r in roots if abs(r.imag) < 1e-9]
    # clamp ruido a 0
    real_roots = [0.0 if abs(x) < 1e-10 else x for x in real_roots]
    return unique_sorted(real_roots, tol=1e-6)

def nsolve_roots(f_expr, x_sym, r_sym, r_val, x_min, x_max, n_seeds=31):
    roots = []
    seeds = np.linspace(x_min, x_max, n_seeds)
    for s in seeds:
        try:
            sol = sp.nsolve(f_expr.subs({r_sym: r_val}), s, tol=1e-14, maxsteps=100)
            sol = float(sol)
            if x_min - 1e-6 <= sol <= x_max + 1e-6:
                roots.append(sol)
        except Exception:
            try:
                s2 = s + (x_max - x_min) / (n_seeds * 3)
                sol = sp.nsolve(f_expr.subs({r_sym: r_val}), (s, s2), tol=1e-14, maxsteps=100)
                sol = float(sol)
                if x_min - 1e-6 <= sol <= x_max + 1e-6:
                    roots.append(sol)
            except Exception:
                pass
    roots = unique_sorted(roots, tol=1e-4)
    # clamp a 0
    roots = [0.0 if abs(x) < 1e-10 else x for x in roots]
    return roots

def find_equilibria(f_expr, x_sym, r_sym, r_val, x_min, x_max):
    """Intenta polinómico primero; si no, usa nsolve."""
    roots = poly_roots_real(f_expr, x_sym, r_sym, r_val)
    if roots is None:
        roots = nsolve_roots(f_expr, x_sym, r_sym, r_val, x_min, x_max)
    return roots

def stability_fx(fx_expr, x_sym, r_sym, x_star, r_val):
    val = float(fx_expr.subs({x_sym: x_star, r_sym: r_val}).evalf())
    if np.isfinite(val):
        if val < 0:  return 'estable', val
        if val > 0:  return 'inestable', val
        return 'neutra', val
    return 'desconocida', np.nan

def auto_steps(r_min, r_max):
    span = max(0.05, float(r_max) - float(r_min))
    steps = int(100 * span)
    return int(np.clip(steps, 151, 801))

def track_branches(Rs, roots_list, stabs_list):
    T = len(Rs); branches = []
    r0_roots = roots_list[0]; r0_stab = stabs_list[0]
    for x0, s0 in zip(r0_roots, r0_stab):
        branches.append({'x':[x0], 'stab':[s0]})
    for t in range(1, T):
        prev_vals = [b['x'][-1] if len(b['x'])==t else np.nan for b in branches]
        new_roots = roots_list[t][:]; new_stab  = stabs_list[t][:]
        unmatched_prev = list(range(len(prev_vals))); unmatched_new  = list(range(len(new_roots)))
        pairs = []
        if unmatched_prev and unmatched_new:
            D = np.zeros((len(unmatched_prev), len(unmatched_new)))
            for i, ip in enumerate(unmatched_prev):
                xp = prev_vals[ip]
                for j, jn in enumerate(unmatched_new):
                    D[i, j] = abs(xp - new_roots[jn])
            while D.size and np.isfinite(D).any():
                i_min, j_min = np.unravel_index(np.argmin(D), D.shape)
                ip = unmatched_prev[i_min]; jn = unmatched_new[j_min]
                pairs.append((ip, jn))
                unmatched_prev.pop(i_min); unmatched_new.pop(j_min)
                if unmatched_prev and unmatched_new:
                    D = np.delete(D, i_min, axis=0); D = np.delete(D, j_min, axis=1)
                else:
                    break
        for b in branches:
            b['x'].append(np.nan); b['stab'].append(None)
        for ip, jn in pairs:
            branches[ip]['x'][-1] = new_roots[jn]; branches[ip]['stab'][-1] = new_stab[jn]
        for jn in unmatched_new:
            b = {'x':[np.nan]*t + [new_roots[jn]], 'stab':[None]*t + [new_stab[jn]]}
            branches.append(b)
    for b in branches:
        b['r'] = list(Rs)
        if len(b['x']) < T:
            pad = T - len(b['x'])
            b['x'] += [np.nan]*pad; b['stab'] += [None]*pad
    return branches

# ----------------- Clase principal -----------------

class BifurcationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bifurcaciones - Modelado y Simulación (x' = f(x, r)) - v4.4")
        self.geometry("1400x800")  # Wider to accommodate two panels
        self.x, self.r = sp.symbols('x r')

        self.f_str = tk.StringVar(value="r*x - x**3")
        self.r_min = tk.DoubleVar(value=-2.0)
        self.r_max = tk.DoubleVar(value=2.0)
        self.r_steps = tk.StringVar(value="")
        self.x_min = tk.DoubleVar(value=-3.0)
        self.x_max = tk.DoubleVar(value=3.0)
        self.phase_r_values = tk.StringVar(value="-0.5, 0, 0.5, 1")

        # almacenamiento de últimos cálculos (añadido, no rompe nada)
        self._last_Rs = None
        self._last_roots_list = None
        self._last_stabs_list = None
        self._last_f = None
        self._last_fx = None
        self._last_phase_rs = None

        self._build_ui(); self._render_latex()

    def _build_ui(self):
        # Create main horizontal layout with two panels
        main_paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Left panel for inputs and results
        self.left_panel = ttk.Frame(main_paned)
        main_paned.add(self.left_panel, weight=1)
        
        # Right panel for plots
        self.right_panel = ttk.Frame(main_paned)
        main_paned.add(self.right_panel, weight=2)
        
        # Create content for each panel
        self._create_left_panel_content()
        self._create_right_panel_content()
        
        # Bottom status bar
        self._create_status_bar()

    def _create_left_panel_content(self):
        """Create all content for the left panel: inputs, keyboard, and results."""
        # Function input section
        self._create_input_section()
        
        # Mathematical keyboard
        self._create_math_keyboard(self.left_panel)
        
        # Results display area
        self._create_results_display(self.left_panel)

    def _create_input_section(self):
        """Create the function input and parameter controls."""
        input_frame = ttk.LabelFrame(self.left_panel, text="Configuración del Sistema")
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(8, 4))
        
        # Function input
        ttk.Label(input_frame, text="f(x, r) =").grid(row=0, column=0, sticky="w", padx=(8, 4), pady=4)
        entry = ttk.Entry(input_frame, textvariable=self.f_str, width=40)
        entry.grid(row=0, column=1, columnspan=2, sticky="we", padx=(0, 8), pady=4)
        entry.bind("<KeyRelease>", lambda e: self._render_latex())
        input_frame.columnconfigure(1, weight=1)

        # Parameter inputs in a more compact layout
        self._create_parameter_inputs_compact(input_frame)
        
        # Control buttons
        self._create_control_buttons_vertical(input_frame)

    def _create_parameter_inputs_compact(self, parent):
        """Create parameter input fields in a compact layout."""
        # r range
        ttk.Label(parent, text="Rango r:").grid(row=1, column=0, sticky="w", padx=(8, 4), pady=2)
        r_frame = ttk.Frame(parent)
        r_frame.grid(row=1, column=1, columnspan=2, sticky="we", padx=(0, 8), pady=2)
        
        ttk.Label(r_frame, text="min:").pack(side=tk.LEFT)
        ttk.Entry(r_frame, textvariable=self.r_min, width=8).pack(side=tk.LEFT, padx=(2, 8))
        ttk.Label(r_frame, text="max:").pack(side=tk.LEFT)
        ttk.Entry(r_frame, textvariable=self.r_max, width=8).pack(side=tk.LEFT, padx=(2, 8))
        ttk.Label(r_frame, text="steps:").pack(side=tk.LEFT)
        ttk.Entry(r_frame, textvariable=self.r_steps, width=8).pack(side=tk.LEFT, padx=2)

        # x range
        ttk.Label(parent, text="Rango x:").grid(row=2, column=0, sticky="w", padx=(8, 4), pady=2)
        x_frame = ttk.Frame(parent)
        x_frame.grid(row=2, column=1, columnspan=2, sticky="we", padx=(0, 8), pady=2)
        
        ttk.Label(x_frame, text="min:").pack(side=tk.LEFT)
        ttk.Entry(x_frame, textvariable=self.x_min, width=8).pack(side=tk.LEFT, padx=(2, 8))
        ttk.Label(x_frame, text="max:").pack(side=tk.LEFT)
        ttk.Entry(x_frame, textvariable=self.x_max, width=8).pack(side=tk.LEFT, padx=2)

        # Phase diagram r values
        ttk.Label(parent, text="r para fases:").grid(row=3, column=0, sticky="w", padx=(8, 4), pady=2)
        ttk.Entry(parent, textvariable=self.phase_r_values, width=40).grid(row=3, column=1, columnspan=2, sticky="we", padx=(0, 8), pady=2)

    def _create_control_buttons_vertical(self, parent):
        """Create control buttons in a vertical layout."""
        button_frame = ttk.LabelFrame(parent, text="Acciones")
        button_frame.grid(row=4, column=0, columnspan=3, sticky="we", padx=8, pady=4)
        
        buttons = [
            ("Calcular y Graficar", self.compute_and_plot),
            ("Paso a paso", self.show_steps),
            ("Limpiar Gráficos", self.clear_plots)
        ]
        
        # Create buttons in a 2x2 grid for better space usage
        for i, (text, command) in enumerate(buttons):
            row = i // 2
            col = i % 2
            ttk.Button(button_frame, text=text, command=command).grid(
                row=row, column=col, padx=4, pady=2, sticky="we"
            )
        
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

    def _create_right_panel_content(self):
        """Create content for the right panel: LaTeX display and plots."""
        # LaTeX display at the top
        latex_frame = ttk.LabelFrame(self.right_panel, text="Función Actual")
        latex_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(8, 4))
        
        self.fig_latex, self.ax_latex, self.canvas_latex = self._create_figure_canvas(
            latex_frame, figsize=(6, 1.2)
        )
        self.ax_latex.axis("off")
        self.canvas_latex.get_tk_widget().pack(side=tk.TOP, fill=tk.X, padx=4, pady=4)
        
        # Main plots area with vertical layout
        plots_paned = ttk.Panedwindow(self.right_panel, orient=tk.VERTICAL)
        plots_paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)
        
        # Bifurcation plot panel
        self._create_bifurcation_plot_panel(plots_paned)
        
        # Phase diagrams and analysis panel
        self._create_analysis_panel(plots_paned)

    def _create_bifurcation_plot_panel(self, parent):
        """Create the bifurcation diagram panel."""
        bif_frame = ttk.LabelFrame(parent, text="Diagrama de Bifurcación")
        parent.add(bif_frame, weight=1)
        
        self.fig_bif, self.ax_bif, self.canvas_bif = self._create_figure_canvas(
            bif_frame, figsize=(8, 4), 
            title="Diagrama de bifurcación", xlabel="r", ylabel="x*"
        )
        self.canvas_bif.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=4, pady=4)

    def _create_analysis_panel(self, parent):
        """Create the phase diagrams and detailed analysis panel."""
        analysis_frame = ttk.Frame(parent)
        parent.add(analysis_frame, weight=1)
        
        # Detailed tabs
        self._create_detailed_tabs_in_frame(analysis_frame)

    def _create_math_keyboard(self, parent):
        """Create mathematical keyboard widget."""
        kb = ttk.LabelFrame(parent, text="Teclado Matemático")
        kb.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        
        keys = ["x","r","(",")","+","-","*","/","^","sin(","cos(","tan(","exp(","log(","sqrt(","abs(","pi","E"]
        
        # Create a frame for the buttons with better organization
        button_frame = ttk.Frame(kb)
        button_frame.pack(padx=8, pady=8)
        
        for i, k in enumerate(keys):
            ttk.Button(button_frame, text=k, width=6, command=lambda s=k: self._insert_token(s)).grid(
                row=i//6, column=i%6, padx=1, pady=1, sticky="we"
            )

    def _create_results_display(self, parent):
        """Create results display area below the mathematical keyboard."""
        results_frame = ttk.LabelFrame(parent, text="Resultados de Cálculo")
        results_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)
        
        # Immediate results text area
        self.txt_results = ScrolledText(results_frame, wrap='word', font=("Consolas", 10), height=15)
        self.txt_results.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Initialize with help text
        self._write_results_header()

    def _create_detailed_tabs_in_frame(self, parent):
        """Create detailed tabs for phase diagrams and step-by-step analysis."""
        self.nb_bottom = ttk.Notebook(parent)
        self.nb_bottom.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Phase diagrams tab
        self.tab_fases = ttk.Frame(self.nb_bottom)
        self.nb_bottom.add(self.tab_fases, text="Diagramas de Fase")
        self.nb_phase = ttk.Notebook(self.tab_fases)
        self.nb_phase.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Add initial help tab
        self._add_phase_help_tab()

        # Detailed step-by-step tab
        self.tab_pasos = ttk.Frame(self.nb_bottom)
        self.nb_bottom.add(self.tab_pasos, text="Análisis Detallado")
        self.txt_pasos = ScrolledText(self.tab_pasos, wrap='word', font=("Consolas", 11))
        self.txt_pasos.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=8)
        self._write_steps_header()

    def _create_results_display(self, parent):
        """Create results display area below the mathematical keyboard."""
        results_frame = ttk.LabelFrame(parent, text="Resultados de Cálculo")
        results_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Immediate results text area
        self.txt_results = ScrolledText(results_frame, wrap='word', font=("Consolas", 10), height=12)
        self.txt_results.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Initialize with help text
        self._write_results_header()

    def _create_right_content(self, parent):
        """Create right content area with plots and detailed tabs."""
        self.pw = ttk.Panedwindow(parent, orient=tk.VERTICAL)
        self.pw.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Top panel for LaTeX and bifurcation plot
        self.top_panel = ttk.Frame(self.pw)
        self.pw.add(self.top_panel, weight=1)
        
        # Bottom panel for detailed tabs
        self.bottom_panel = ttk.Frame(self.pw)
        self.pw.add(self.bottom_panel, weight=3)
        
        # LaTeX display
        self.fig_latex, self.ax_latex, self.canvas_latex = self._create_figure_canvas(
            self.top_panel, figsize=(4.8, 1.0)
        )
        self.ax_latex.axis("off")
        self.canvas_latex.get_tk_widget().pack(side=tk.TOP, fill=tk.X)

        # Bifurcation plot
        self.fig_bif, self.ax_bif, self.canvas_bif = self._create_figure_canvas(
            self.top_panel, figsize=(7.0, 3.2), 
            title="Diagrama de bifurcación", xlabel="r", ylabel="x*"
        )
        self.canvas_bif.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Detailed tabs
        self._create_detailed_tabs()

    def _create_detailed_tabs(self):
        """Create detailed tabs for phase diagrams and step-by-step analysis."""
        self.nb_bottom = ttk.Notebook(self.bottom_panel)
        self.nb_bottom.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Phase diagrams tab
        self.tab_fases = ttk.Frame(self.nb_bottom)
        self.nb_bottom.add(self.tab_fases, text="Diagramas de Fase")
        self.nb_phase = ttk.Notebook(self.tab_fases)
        self.nb_phase.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Add initial help tab
        self._add_phase_help_tab()

        # Detailed step-by-step tab
        self.tab_pasos = ttk.Frame(self.nb_bottom)
        self.nb_bottom.add(self.tab_pasos, text="Análisis Detallado")
        self.txt_pasos = ScrolledText(self.tab_pasos, wrap='word', font=("Consolas", 11))
        self.txt_pasos.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=8)
        self._write_steps_header()

    def _create_status_bar(self):
        """Create bottom status bar."""
        bottom_status = ttk.Frame(self)
        bottom_status.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=6)
        self.status = tk.StringVar(value="Listo")
        ttk.Label(bottom_status, textvariable=self.status).pack(side=tk.LEFT)

    def _insert_token(self, token):
        self.f_str.set(self.f_str.get() + token)
        self._render_latex()

    def _write_results_header(self):
        """Write header information in the results display area."""
        self.txt_results.config(state='normal')
        self.txt_results.delete('1.0', tk.END)
        self.txt_results.insert(tk.END, "== RESULTADOS DE CÁLCULO ==\n\n")
        self.txt_results.insert(tk.END, "Los resultados del último cálculo aparecerán aquí.\n")
        self.txt_results.insert(tk.END, "• Presiona 'Calcular y Graficar' para ver los equilibrios\n")
        self.txt_results.insert(tk.END, "• Presiona 'Paso a paso' para análisis detallado\n\n")
        self.txt_results.config(state='disabled')

    def _update_results_display(self, f_expr, fx_expr, sample_rs):
        """Update the immediate results display with calculation summary."""
        self.txt_results.config(state='normal')
        self.txt_results.delete('1.0', tk.END)
        
        self.txt_results.insert(tk.END, "== RESULTADOS DE CÁLCULO ==\n\n")
        self.txt_results.insert(tk.END, f"Función: f(x,r) = {f_expr}\n")
        self.txt_results.insert(tk.END, f"Derivada: f_x = {fx_expr}\n\n")
        
        # Show bifurcation information if available
        if hasattr(self, '_last_bifurcations') and self._last_bifurcations:
            self.txt_results.insert(tk.END, "BIFURCACIONES DETECTADAS:\n")
            self.txt_results.insert(tk.END, "=" * 40 + "\n")
            for r_bif, bif_type in self._last_bifurcations:
                self.txt_results.insert(tk.END, f"• r ≈ {r_bif:.6f}: {bif_type}\n")
            self.txt_results.insert(tk.END, "\n")
        else:
            self.txt_results.insert(tk.END, "No se detectaron bifurcaciones en el rango.\n\n")
        
        # Show equilibria for sample r values
        self.txt_results.insert(tk.END, "Equilibrios para valores muestra de r:\n")
        self.txt_results.insert(tk.END, "-" * 40 + "\n")
        
        x_min, x_max = float(self.x_min.get()), float(self.x_max.get())
        
        for r_val in sample_rs:
            roots = find_equilibria(f_expr, self.x, self.r, r_val, x_min, x_max)
            self.txt_results.insert(tk.END, f"\nr = {r_val:.3f}:\n")
            
            if not roots:
                self.txt_results.insert(tk.END, "  No hay equilibrios en el rango\n")
            else:
                for xs_star in roots:
                    stab, slope = stability_fx(fx_expr, self.x, self.r, xs_star, r_val)
                    stab_symbol = "●" if stab == 'estable' else "○" if stab == 'inestable' else "◐"
                    self.txt_results.insert(tk.END, f"  {stab_symbol} x* = {xs_star:.6f} ({stab})\n")
        
        self.txt_results.insert(tk.END, f"\n{'●'} = Estable, {'○'} = Inestable, {'◐'} = Neutro\n")
        self.txt_results.insert(tk.END, "\nPara análisis completo, usar 'Paso a paso'.\n")
        
        # Auto-scroll to top
        self.txt_results.see('1.0')
        self.txt_results.config(state='disabled')

    def _create_figure_canvas(self, parent, figsize, title=None, xlabel=None, ylabel=None):
        """Helper method to create matplotlib figure and canvas with common setup."""
        fig = Figure(figsize=figsize)
        ax = fig.add_subplot(111)
        
        if title:
            ax.set_title(title)
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)
            
        canvas = FigureCanvasTkAgg(fig, master=parent)
        return fig, ax, canvas

    def _create_phase_plot(self, ax, f_expr, fx_expr, r_val, title):
        """Helper method to create a single phase plot with equilibria and flow arrows."""
        x_min = float(self.x_min.get())
        x_max = float(self.x_max.get())
        
        # Plot the function
        xs = np.linspace(x_min, x_max, 800)
        f_num = sp.lambdify((self.x, self.r), f_expr, 'numpy')
        ys = f_num(xs, r_val)
        ax.plot(xs, ys, linewidth=1.1)
        ax.set_title(title)
        ax.set_xlabel("x")
        ax.set_ylabel("x'")
        
        # Add equilibrium points
        roots = find_equilibria(f_expr, self.x, self.r, r_val, x_min, x_max)
        for xs_star in roots:
            stab, _ = stability_fx(fx_expr, self.x, self.r, xs_star, r_val)
            if stab == 'estable':
                ax.plot([xs_star], [0], marker='o', markersize=9, color='blue')
            else:
                ax.plot([xs_star], [0], marker='o', markersize=9, markerfacecolor='white',
                        markeredgecolor='red', markeredgewidth=2)
        
        # Add flow arrows
        for xp in np.linspace(x_min, x_max, 27):
            val = float(f_num(xp, r_val))
            dx = (x_max - x_min) / 40.0
            if np.isfinite(val) and abs(val) > 1e-8:
                x0 = xp - dx/2.0
                x1 = xp + dx/2.0
                if val < 0:
                    x0, x1 = x1, x0
                ax.annotate("", xy=(x1, 0), xytext=(x0, 0), arrowprops=dict(arrowstyle="->", lw=1.0))
        
        ax.axhline(0, color='k', linewidth=1.0, alpha=0.65)
        ax.grid(True)

    def _detect_bifurcation_type(self, f_expr, fx_expr, fxx_expr, r_values, equilibria_list):
        """Detect and classify bifurcation types with improved accuracy."""
        bifurcations = []
        
        # Look for changes in number of equilibria or stability
        for i in range(len(r_values) - 1):
            r_curr = r_values[i]
            r_next = r_values[i + 1]
            eq_curr = equilibria_list[i]
            eq_next = equilibria_list[i + 1]
            
            # Check for changes in number of equilibria
            if len(eq_curr) != len(eq_next):
                r_bif = (r_curr + r_next) / 2
                bif_type = self._analyze_bifurcation_at_point(
                    f_expr, fx_expr, fxx_expr, r_bif, r_curr, r_next
                )
                if bif_type:
                    bifurcations.append((r_bif, bif_type))
        
        return bifurcations

    def _analyze_bifurcation_at_point(self, f_expr, fx_expr, fxx_expr, r_bif, r_before, r_after):
        """Analyze the type of bifurcation at a specific point using multiple criteria."""
        try:
            x_min, x_max = float(self.x_min.get()), float(self.x_max.get())
            
            # Use the actual r_before and r_after values to get equilibria
            # This is more accurate than using a fixed delta
            eq_before = find_equilibria(f_expr, self.x, self.r, r_before, x_min, x_max)
            eq_at = find_equilibria(f_expr, self.x, self.r, r_bif, x_min, x_max)
            eq_after = find_equilibria(f_expr, self.x, self.r, r_after, x_min, x_max)
            
            n_before, n_at, n_after = len(eq_before), len(eq_at), len(eq_after)
            
            # Simple but robust detection based on equilibria count changes
            
            # Pitchfork: 1 becomes 3 or 3 becomes 1
            if (n_before == 1 and n_after == 3) or (n_before == 3 and n_after == 1):
                return "Bifurcación horquilla (pitchfork)"
            
            # Transcritical: same number of equilibria (usually 2) but they exchange stability/position
            if n_before == n_after and n_before >= 2:
                # For transcritical, equilibria don't disappear/appear, they cross
                if len(eq_before) >= 2 and len(eq_after) >= 2:
                    # Sort equilibria to compare positions
                    eq_before_sorted = sorted([float(eq) for eq in eq_before])
                    eq_after_sorted = sorted([float(eq) for eq in eq_after])
                    
                    # Check if equilibria actually "cross" by comparing their relative positions
                    # In transcritical bifurcation, the relative ordering can change
                    dist_before = abs(eq_before_sorted[-1] - eq_before_sorted[0])  # Distance between outermost
                    dist_after = abs(eq_after_sorted[-1] - eq_after_sorted[0])
                    
                    # Also check if the center point changes (equilibria cross)
                    center_before = sum(eq_before_sorted) / len(eq_before_sorted)
                    center_after = sum(eq_after_sorted) / len(eq_after_sorted)
                    
                    # If positions or spacing changed significantly, it's transcritical
                    if abs(center_before - center_after) > 0.001 or abs(dist_before - dist_after) > 0.001:
                        return "Bifurcación transcrítica"
            
            # Saddle-node: creation or destruction of equilibria
            # Check this AFTER transcritical to avoid false positives
            if (n_before > n_after and n_before - n_after >= 1) or \
               (n_after > n_before and n_after - n_before >= 1):
                return "Bifurcación silla-nodo"
            
            # Default classification based on count change
            if n_after > n_before:
                return "Aparición de equilibrios"
            elif n_after < n_before:
                return "Desaparición de equilibrios"
            else:
                return "Cambio de estabilidad"
                
        except Exception as e:
            return f"Bifurcación no clasificada"

    def _is_saddle_node(self, n_before, n_at, n_after, eq_before, eq_at, eq_after):
        """Check if it's a saddle-node bifurcation."""
        # Classic saddle-node: 2 → 1 → 0 or 0 → 1 → 2
        if (n_before == 2 and n_at == 1 and n_after == 0) or \
           (n_before == 0 and n_at == 1 and n_after == 2):
            return True
        
        # More general: difference of exactly 2 equilibria
        if abs(n_after - n_before) == 2 and n_at == min(n_before, n_after) + 1:
            return True
            
        return False

    def _is_transcritical(self, f_expr, fx_expr, r_bif, eq_before, eq_after, delta):
        """Check if it's a transcritical bifurcation."""
        if len(eq_before) != len(eq_after) or len(eq_before) != 2:
            return False
        
        try:
            # In transcritical bifurcation, we have exactly 2 equilibria before and after
            # and they "cross" - their relative positions swap
            eq_before_sorted = sorted(eq_before)
            eq_after_sorted = sorted(eq_after)
            
            # Check if equilibria positions actually crossed (significant position change)
            position_change = abs((eq_before_sorted[0] - eq_after_sorted[0]) - 
                                (eq_before_sorted[1] - eq_after_sorted[1]))
            
            # If positions changed significantly, it's likely transcritical
            if position_change > 0.01:
                # Additional check: stability should exchange
                stab_before = []
                stab_after = []
                
                for x_eq in eq_before:
                    stab, _ = stability_fx(fx_expr, self.x, self.r, x_eq, r_bif - delta)
                    stab_before.append(stab)
                    
                for x_eq in eq_after:
                    stab, _ = stability_fx(fx_expr, self.x, self.r, x_eq, r_bif + delta)
                    stab_after.append(stab)
                
                # Count stable equilibria before and after
                stable_before = stab_before.count('estable')
                stable_after = stab_after.count('estable')
                
                # In true transcritical, stability is conserved
                return stable_before == stable_after
            
            return False
            
        except:
            return False

    def _is_pitchfork(self, f_expr, fx_expr, fxx_expr, r_bif, n_before, n_after, eq_before, eq_after):
        """Check if it's a pitchfork bifurcation."""
        # Supercritical pitchfork: 1 → 3 (one equilibrium becomes three)
        # Subcritical pitchfork: 3 → 1 (three equilibria become one)
        if not ((n_before == 1 and n_after == 3) or (n_before == 3 and n_after == 1)):
            return False
        
        try:
            # Additional check: in pitchfork, there should be symmetry
            # The system should have f(-x,r) = -f(x,r) or similar symmetry
            
            # Check if the middle equilibrium (usually at x=0) remains
            if n_before == 1 and n_after == 3:
                # The original equilibrium should still exist among the three
                original_eq = eq_before[0]
                # Check if original equilibrium is close to one of the new ones
                for new_eq in eq_after:
                    if abs(new_eq - original_eq) < 0.01:
                        return True
            
            elif n_before == 3 and n_after == 1:
                # Three equilibria should collapse to the middle one
                final_eq = eq_after[0]
                # Check if final equilibrium is close to the middle of the three
                if len(eq_before) == 3:
                    middle_eq = sorted(eq_before)[1]  # Middle equilibrium
                    if abs(final_eq - middle_eq) < 0.01:
                        return True
            
            return False
            
        except:
            return False

    def _test_bifurcation_detection(self):
        """Test the bifurcation detection with known examples."""
        test_results = []
        
        # Test 1: Saddle-node bifurcation - f(x,r) = r + x^2
        print("Testing bifurcation detection...")
        test_results.append(self._test_saddle_node())
        
        # Test 2: Transcritical bifurcation - f(x,r) = rx - x^2  
        test_results.append(self._test_transcritical())
        
        # Test 3: Pitchfork bifurcation - f(x,r) = rx - x^3
        test_results.append(self._test_pitchfork())
        
        return test_results

    def _test_saddle_node(self):
        """Test with f(x,r) = r + x^2 (saddle-node at r=0)."""
        try:
            f_test = self.r + self.x**2
            fx_test = sp.diff(f_test, self.x)
            fxx_test = sp.diff(fx_test, self.x)
            
            r_vals = np.linspace(-0.1, 0.1, 21)
            eq_list = []
            for r_val in r_vals:
                eq = find_equilibria(f_test, self.x, self.r, r_val, -2, 2)
                eq_list.append(eq)
            
            bifurcations = self._detect_bifurcation_type(f_test, fx_test, fxx_test, r_vals, eq_list)
            
            # Should detect saddle-node near r=0
            for r_bif, bif_type in bifurcations:
                if abs(r_bif) < 0.05 and "silla-nodo" in bif_type.lower():
                    return f"✓ Saddle-node test passed: {bif_type} at r={r_bif:.4f}"
            
            return f"✗ Saddle-node test failed: {bifurcations}"
        except Exception as e:
            return f"✗ Saddle-node test error: {e}"

    def _test_transcritical(self):
        """Test with f(x,r) = rx - x^2 (transcritical at r=0)."""
        try:
            f_test = self.r * self.x - self.x**2
            fx_test = sp.diff(f_test, self.x)
            fxx_test = sp.diff(fx_test, self.x)
            
            r_vals = np.linspace(-0.1, 0.1, 21)
            eq_list = []
            for r_val in r_vals:
                eq = find_equilibria(f_test, self.x, self.r, r_val, -2, 2)
                eq_list.append(eq)
            
            bifurcations = self._detect_bifurcation_type(f_test, fx_test, fxx_test, r_vals, eq_list)
            
            # Should detect transcritical near r=0
            for r_bif, bif_type in bifurcations:
                if abs(r_bif) < 0.05 and "transcrítica" in bif_type.lower():
                    return f"✓ Transcritical test passed: {bif_type} at r={r_bif:.4f}"
            
            return f"✗ Transcritical test failed: {bifurcations}"
        except Exception as e:
            return f"✗ Transcritical test error: {e}"

    def _test_pitchfork(self):
        """Test with f(x,r) = rx - x^3 (pitchfork at r=0)."""
        try:
            f_test = self.r * self.x - self.x**3
            fx_test = sp.diff(f_test, self.x)
            fxx_test = sp.diff(fx_test, self.x)
            
            r_vals = np.linspace(-0.1, 0.1, 21)
            eq_list = []
            for r_val in r_vals:
                eq = find_equilibria(f_test, self.x, self.r, r_val, -2, 2)
                eq_list.append(eq)
            
            bifurcations = self._detect_bifurcation_type(f_test, fx_test, fxx_test, r_vals, eq_list)
            
            # Should detect pitchfork near r=0
            for r_bif, bif_type in bifurcations:
                if abs(r_bif) < 0.05 and ("horquilla" in bif_type.lower() or "pitchfork" in bif_type.lower()):
                    return f"✓ Pitchfork test passed: {bif_type} at r={r_bif:.4f}"
            
            return f"✗ Pitchfork test failed: {bifurcations}"
        except Exception as e:
            return f"✗ Pitchfork test error: {e}"

    def _detect_critical_r(self):
        """Detect critical r value where bifurcation occurs."""
        try:
            Rs = self._last_Rs if hasattr(self, '_last_Rs') else np.linspace(
                float(self.r_min.get()), float(self.r_max.get()), 201
            )
            roots_list = self._last_roots_list if hasattr(self, '_last_roots_list') else []
            
            if not roots_list:
                return float(self.r_min.get())
            
            # Find where number of roots changes
            for i in range(len(roots_list) - 1):
                if len(roots_list[i]) != len(roots_list[i + 1]):
                    return Rs[i + (Rs[i + 1] - Rs[i]) / 2]
            
            # If no count change, look for stability changes
            if hasattr(self, '_last_stabs_list'):
                stabs_list = self._last_stabs_list
                for i in range(len(stabs_list) - 1):
                    if len(stabs_list[i]) == len(stabs_list[i + 1]):
                        for j in range(len(stabs_list[i])):
                            if j < len(stabs_list[i + 1]) and stabs_list[i][j] != stabs_list[i + 1][j]:
                                return Rs[i + (Rs[i + 1] - Rs[i]) / 2]
            
            return Rs[len(Rs) // 2]  # Default to middle value
        except:
            return 0.0

    def _create_phase_tabs(self, f_expr, fx_expr, r_list):
        """Create phase diagram tabs for each r value in the r_list."""
        for i, r_val in enumerate(r_list):
            # Create tab frame
            tab_frame = ttk.Frame(self.nb_phase)
            self.nb_phase.add(tab_frame, text=f"r = {r_val:g}")
            
            # Create the phase plot in this tab
            fig, ax, canvas = self._create_figure_canvas(
                tab_frame, figsize=(8, 5),
                title=f"Diagrama de fase 1D (r = {r_val:g})",
                xlabel="x", ylabel="x'"
            )
            
            # Use the helper method to populate the plot
            self._create_phase_plot(ax, f_expr, fx_expr, r_val, f"Diagrama de fase 1D (r = {r_val:g})")
            
            # Add click event to open individual window
            def make_click_handler(r_val, f_expr, fx_expr):
                return lambda event: self._open_phase_window(f_expr, fx_expr, r_val)
            
            fig.canvas.mpl_connect('button_press_event', make_click_handler(r_val, f_expr, fx_expr))
            
            fig.tight_layout()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=4, pady=4)
            canvas.draw()

    def _add_phase_help_tab(self):
        """Add a help tab when no phase diagrams are available."""
        help_frame = ttk.Frame(self.nb_phase)
        self.nb_phase.add(help_frame, text="Información")
        
        help_text = ScrolledText(help_frame, wrap='word', font=("Arial", 11))
        help_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        help_content = """DIAGRAMAS DE FASE

Para ver los diagramas de fase:

1. Ingresa una función f(x,r) en el campo superior
2. Define los valores de r en el campo "r para diagramas de fase"
   Ejemplo: -0.5, 0, 0.5, 1
3. Presiona "Calcular y Graficar"

Los diagramas de fase mostrarán:
• Línea azul: la función f(x,r)
• Puntos azules sólidos ●: equilibrios estables
• Puntos rojos vacíos ○: equilibrios inestables  
• Flechas: dirección del flujo dinámico

También puedes:
• Hacer clic en cualquier diagrama para abrirlo en ventana separada
• Usar "Mostrar fases divididas" para ver 3 fases simultáneas
• Consultar "Paso a paso" para análisis detallado
"""
        
        help_text.insert('1.0', help_content)
        help_text.config(state='disabled')

    def _render_latex(self):
        try:
            f_expr = sympify(self.f_str.get(), locals={'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
                                                       'exp': sp.exp, 'log': sp.log, 'sqrt': sp.sqrt,
                                                       'abs': sp.Abs, 'pi': sp.pi, 'E': sp.E})
            latex = sp.latex(sp.Eq(sp.Symbol("x'"), f_expr))
        except Exception:
            latex = r"\text{Error en la función}"
        self.ax_latex.clear(); self.ax_latex.axis('off')
        self.ax_latex.text(0.02, 0.5, f"${latex}$", fontsize=15, va='center', ha='left')
        self.canvas_latex.draw_idle()

    def clear_plots(self):
        """Clear all plots and reset displays."""
        self.ax_bif.clear()
        self.ax_bif.set_title("Diagrama de bifurcación")
        self.ax_bif.set_xlabel("r")
        self.ax_bif.set_ylabel("x*")
        self.canvas_bif.draw_idle()
        
        # Clear phase tabs
        for tab_id in self.nb_phase.tabs():
            self.nb_phase.forget(tab_id)
        
        # Add help tab back
        self._add_phase_help_tab()
        
        # Reset displays
        self._write_steps_header()
        self._write_results_header()
        
        # Clear bifurcation data
        self._last_bifurcations = []
        
        self.status.set("Gráficos limpiados.")

    def _write_steps_header(self):
        self.txt_pasos.config(state='normal'); self.txt_pasos.delete('1.0', tk.END)
        self.txt_pasos.insert(tk.END, "== PASO A PASO: Bifurcaciones 1D ==\n\n")
        self.txt_pasos.insert(tk.END, "Puntos críticos = soluciones de f(x, r) = 0.\n")
        self.txt_pasos.insert(tk.END, "Estabilidad local: signo de f_x(x*, r):\n")
        self.txt_pasos.insert(tk.END, "  • f_x < 0  → Estable (atractor)\n")
        self.txt_pasos.insert(tk.END, "  • f_x > 0  → Inestable (repulsor)\n")
        self.txt_pasos.insert(tk.END, "  • f_x = 0  → No hiperbólico\n\n")
        self.txt_pasos.config(state='disabled')

    def show_steps(self):
        try:
            _ = self._last_f
        except AttributeError:
            self.compute_and_plot()
        try:
            self._write_steps_detail(); self.nb_bottom.select(self.tab_pasos)
        except Exception:
            self._write_steps_header()

    # ----------------- Cálculo principal (casi idéntico) -----------------
    def compute_and_plot(self):
        try:
            f_expr = sympify(self.f_str.get(), locals={'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
                                                       'exp': sp.exp, 'log': sp.log, 'sqrt': sp.sqrt,
                                                       'abs': sp.Abs, 'pi': sp.pi, 'E': sp.E})
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo interpretar f(x, r).\n{e}"); return

        x, r = self.x, self.r; fx_expr = diff(f_expr, x)

        r_min = float(self.r_min.get()); r_max = float(self.r_max.get())
        try:
            r_steps_val = int(self.r_steps.get()); assert r_steps_val > 0
        except Exception:
            r_steps_val = auto_steps(r_min, r_max)

        x_min = float(self.x_min.get()); x_max = float(self.x_max.get())

        Rs = np.linspace(r_min, r_max, r_steps_val)

        # Raíces por r (polinómico si es posible)
        roots_list = []; stabs_list = []
        for rv in Rs:
            roots = find_equilibria(f_expr, x, r, rv, x_min, x_max)
            stabs = []
            for xs_star in roots:
                stab, _ = stability_fx(fx_expr, x, r, xs_star, rv)
                stabs.append(stab)
            roots_list.append(roots); stabs_list.append(stabs)

        # Guardar para uso posterior (para la función de fases divididas / paso a paso)
        self._last_Rs = Rs
        self._last_roots_list = roots_list
        self._last_stabs_list = stabs_list
        self._last_f = f_expr
        self._last_fx = fx_expr

        branches = track_branches(Rs, roots_list, stabs_list)

        # Plot de ramas (solo líneas) - idéntico a original
        self.ax_bif.clear(); self.ax_bif.set_title("Diagrama de bifurcación")
        self.ax_bif.set_xlabel("r"); self.ax_bif.set_ylabel("x*")
        any_est=False; any_ins=False
        for b in branches:
            r_arr = np.array(b['r']); x_arr = np.array(b['x'], dtype=float)
            x_arr[np.abs(x_arr) < 1e-10] = 0.0  # clamp
            stab_arr = np.array([s if s is not None else '' for s in b['stab']], dtype=object)
            xs_est = np.where(stab_arr == 'estable', x_arr, np.nan)
            xs_ins = np.where(stab_arr == 'inestable', x_arr, np.nan)
            if np.isfinite(xs_est).any():
                self.ax_bif.plot(r_arr, xs_est, linestyle='solid', linewidth=2.0, color='blue'); any_est=True
            if np.isfinite(xs_ins).any():
                self.ax_bif.plot(r_arr, xs_ins, linestyle='dotted', linewidth=2.0, color='red'); any_ins=True
        if any_est or any_ins:
            from matplotlib.lines import Line2D
            handles=[]
            if any_est: handles.append(Line2D([0],[0], color='blue', lw=2, ls='solid', label='Estable'))
            if any_ins: handles.append(Line2D([0],[0], color='red', lw=2, ls='dotted', label='Inestable'))
            self.ax_bif.legend(handles=handles, loc='best')
        self.canvas_bif.draw_idle()

        # Detectar y mostrar bifurcaciones
        fxx_expr = diff(fx_expr, x)  # Segunda derivada para análisis más detallado
        bifurcations = self._detect_bifurcation_type(f_expr, fx_expr, fxx_expr, Rs, roots_list)
        self._last_bifurcations = bifurcations
        
        # Marcar bifurcaciones en el diagrama
        for r_bif, bif_type in bifurcations:
            self.ax_bif.axvline(r_bif, color='orange', linestyle='--', alpha=0.7, linewidth=2)
            self.ax_bif.text(r_bif, self.ax_bif.get_ylim()[1] * 0.9, 
                           f'r≈{r_bif:.3f}\n{bif_type}', 
                           rotation=0, ha='center', va='top', 
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='orange', alpha=0.7),
                           fontsize=9)
        
        if bifurcations:
            self.canvas_bif.draw_idle()

        # Actualizar mensaje de estado con información de bifurcaciones
        bif_count = len(bifurcations)
        if bif_count > 0:
            bif_summary = f"Detectadas {bif_count} bifurcación(es): " + \
                         ", ".join([f"{bt} (r≈{rb:.3f})" for rb, bt in bifurcations[:2]])
            if bif_count > 2:
                bif_summary += f" y {bif_count-2} más..."
            self.status.set(f"Cálculo completado. {bif_summary}")
        else:
            # Heurística: busca valores de r donde cambie la cantidad de raíces reales
            counts = [len(rr) for rr in roots_list]
            if max(counts) != min(counts):
                self.status.set(f"Cálculo completado. r_steps={r_steps_val}")
            else:
                # si todo el rango tiene el mismo número de raíces, advertimos revisar r_min/r_max
                self.status.set(f"Cálculo completado. r_steps={r_steps_val}. Nota: la cantidad de equilibrios no cambia en el rango; revisá r_min/r_max si esperabas una bifurcación.")

        # ----------------------------------------------------------
        # NOTA: aquí antes se generaban las pestañas de fases dentro de la interfaz.
        # Se conserva el cálculo de `r_list` y se guardan los valores, pero NO
        # se crean las pestañas (esa funcionalidad la reemplaza el botón
        # "Mostrar fases divididas" que abre una ventana con 3 subplots).
        # ----------------------------------------------------------
        # r list para fases
        try:
            r_list = []
            for tok in self.phase_r_values.get().replace(';', ',').replace(' ', ',').split(','):
                tok = tok.strip()
                if tok: r_list.append(float(tok))
        except Exception:
            r_list = [0.0]

        # Guardar lista de r para fases y crear pestañas
        self._last_phase_rs = r_list
        
        # Clear existing phase tabs
        for tab_id in self.nb_phase.tabs():
            self.nb_phase.forget(tab_id)
        
        # Create phase diagram tabs for each r value
        self._create_phase_tabs(f_expr, fx_expr, r_list)

        # Guardar también la muestra de Rs (inicio/medio/fin) para paso a paso
        self._last_scan_Rs = [Rs[0], Rs[len(Rs)//2], Rs[-1]]
        
        # Actualizar área de resultados inmediatos
        self._update_results_display(f_expr, fx_expr, self._last_scan_Rs)
        
        # y escribir paso a paso
        self._write_steps_detail()

    # ----------------- ventana de fase individual (original) -----------------
    def _open_phase_window(self, f_expr, fx_expr, rv):
        x, r = self.x, self.r
        x_min = float(self.x_min.get())
        x_max = float(self.x_max.get())
        xs = np.linspace(x_min, x_max, 800)
        f_num = sp.lambdify((x, r), f_expr, 'numpy')
        
        win = tk.Toplevel(self)
        win.title(f"Diagrama de fase (r={rv:g})")
        win.geometry("900x600")
        
        fig, ax, canvas = self._create_figure_canvas(
            win, figsize=(9.0, 6.0),
            title=f"Diagrama de fase 1D (r = {rv:g})",
            xlabel="x", ylabel="x'"
        )
        
        ax.plot(xs, f_num(xs, rv))
        
        roots = find_equilibria(f_expr, x, r, rv, x_min, x_max)
        for xs_star in roots:
            stab, _ = stability_fx(fx_expr, x, r, xs_star, rv)
            if stab == 'estable':
                ax.plot([xs_star], [0], marker='o', markersize=10, color='blue')
            else:
                ax.plot([xs_star], [0], marker='o', markersize=10, markerfacecolor='white',
                        markeredgecolor='red', markeredgewidth=2)
        
        for xp in np.linspace(x_min, x_max, 31):
            val = float(f_num(xp, rv))
            dx = (x_max - x_min) / 36.0
            if np.isfinite(val) and abs(val) > 1e-8:
                x0 = xp - dx/2.0
                x1 = xp + dx/2.0
                if val < 0: 
                    x0, x1 = x1, x0
                ax.annotate("", xy=(x1, 0), xytext=(x0, 0), arrowprops=dict(arrowstyle="->", lw=1.1))
        
        ax.axhline(0, color='k', linewidth=1.0, alpha=0.65)
        fig.tight_layout()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        canvas.draw()

    # ----------------- Paso a paso y escritura de detalle -----------------
    def _write_steps_detail(self):
        self.txt_pasos.config(state='normal'); self._write_steps_header()
        f_expr, fx_expr = self._last_f, self._last_fx; x, r = self.x, self.r

        self.txt_pasos.insert(tk.END, "1) Sistema 1D:  x' = f(x, r)\n\n")
        self.txt_pasos.insert(tk.END, f"2) f(x, r) = {sp.sstr(f_expr)}\n")
        self.txt_pasos.insert(tk.END, f"   LaTeX:  ${sp.latex(f_expr)}$\n\n")
        self.txt_pasos.insert(tk.END, f"3) Derivada local:  f_x(x, r) = {sp.sstr(fx_expr)}\n")
        self.txt_pasos.insert(tk.END, f"   LaTeX:  ${sp.latex(fx_expr)}$\n\n")
        self.txt_pasos.insert(tk.END, "4) Procedimiento para hallar puntos críticos:\n")
        self.txt_pasos.insert(tk.END, "   • Si f es polinómica en x → se forman los coeficientes en x, se evalúan en r,\n")
        self.txt_pasos.insert(tk.END, "     y se hallan las raíces reales con np.roots.\n")
        self.txt_pasos.insert(tk.END, "   • Si no lo es → se usa nsolve desde múltiples semillas en el rango [x_min, x_max].\n\n")

        # Agregar información de bifurcaciones detectadas
        if hasattr(self, '_last_bifurcations') and self._last_bifurcations:
            self.txt_pasos.insert(tk.END, "4) BIFURCACIONES DETECTADAS:\n")
            for i, (r_bif, bif_type) in enumerate(self._last_bifurcations, 1):
                self.txt_pasos.insert(tk.END, f"   {i}) r ≈ {r_bif:.6f}: {bif_type}\n")
                
                # Análisis local alrededor de la bifurcación
                x_min = float(self.x_min.get()); x_max = float(self.x_max.get())
                delta_r = 0.01
                
                eq_before = find_equilibria(f_expr, x, r, r_bif - delta_r, x_min, x_max)
                eq_at = find_equilibria(f_expr, x, r, r_bif, x_min, x_max)
                eq_after = find_equilibria(f_expr, x, r, r_bif + delta_r, x_min, x_max)
                
                self.txt_pasos.insert(tk.END, f"      Antes (r={r_bif-delta_r:.3f}): {len(eq_before)} equilibrio(s)\n")
                self.txt_pasos.insert(tk.END, f"      En bifurcación (r={r_bif:.3f}): {len(eq_at)} equilibrio(s)\n") 
                self.txt_pasos.insert(tk.END, f"      Después (r={r_bif+delta_r:.3f}): {len(eq_after)} equilibrio(s)\n")
                self.txt_pasos.insert(tk.END, "\n")
            
            self.txt_pasos.insert(tk.END, "\n")
        else:
            self.txt_pasos.insert(tk.END, "4) No se detectaron bifurcaciones en el rango analizado.\n\n")

        x_min = float(self.x_min.get()); x_max = float(self.x_max.get())

        self.txt_pasos.insert(tk.END, "5) Equilibrios y estabilidad para valores de r de los diagramas de fase:\n")
        for rv in self._last_phase_rs:
            self.txt_pasos.insert(tk.END, f"   - r = {rv:.6g}\n")
            roots = find_equilibria(f_expr, x, r, rv, x_min, x_max)
            if not roots:
                self.txt_pasos.insert(tk.END, "       (Sin raíces reales en el rango de x)\n")
            for xs_star in roots:
                stab, slope = stability_fx(fx_expr, x, r, xs_star, rv)
                self.txt_pasos.insert(tk.END, f"       x* = {xs_star:.9g}   f_x(x*,r) = {slope:.6g}  →  {stab.upper()}\n")
            self.txt_pasos.insert(tk.END, "\n")

        Rs = [self.r_min.get(), 0.5*(self.r_min.get()+self.r_max.get()), self.r_max.get()]
        self.txt_pasos.insert(tk.END, "6) Equilibrios y estabilidad (inicio / medio / fin del barrido de r):\n")
        labels = ["   • Inicio:", "   • Medio:", "   • Fin:"]
        for lab, rv in zip(labels, Rs):
            self.txt_pasos.insert(tk.END, f"{lab} r = {rv:.6g}\n")
            roots = find_equilibria(f_expr, x, r, rv, x_min, x_max)
            if not roots:
                self.txt_pasos.insert(tk.END, "       (Sin raíces reales en el rango de x)\n")
            for xs_star in roots:
                stab, slope = stability_fx(fx_expr, x, r, xs_star, rv)
                self.txt_pasos.insert(tk.END, f"       x* = {xs_star:.9g}   f_x(x*,r) = {slope:.6g}  →  {stab.upper()}\n")
            self.txt_pasos.insert(tk.END, "\n")

        self.txt_pasos.config(state='disabled')

# ----------------- ejecución -----------------

if __name__ == "__main__":
    app = BifurcationApp()
    app.mainloop()

