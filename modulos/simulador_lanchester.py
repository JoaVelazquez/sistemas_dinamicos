"""
Simulador de Modelos de Lanchester
Basado en los simuladores de sistemas dinámicos

Modelos incluidos:
- Lanchester Lineal (guerrilla/antiguo)
- Lanchester Cuadrático (moderno/concentrado)
- Modelo con Recursos Económicos
- Modelo de Comercio/Mercenarios
- Modelo con Fatiga y Refuerzos

Parámetros:
- Blue inicial, Red inicial: tropas iniciales
- α (alfa), β (beta): tasas de atrito
- Tipo de Lanchester: lineal, cuadrático, mixto
- Fatiga: desgaste por tiempo
- Refuerzos: llegada de tropas nuevas
- Recursos económicos: presupuesto y costos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.integrate import odeint
import warnings
warnings.filterwarnings('ignore')


class LanchesterSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Modelos de Lanchester")
        self.root.geometry("1500x900")
        
        # Initial conditions
        self.blue_initial = tk.DoubleVar(value=100.0)
        self.red_initial = tk.DoubleVar(value=80.0)
        
        # Combat effectiveness parameters
        self.alpha = tk.DoubleVar(value=0.05)  # Red's effectiveness against Blue
        self.beta = tk.DoubleVar(value=0.04)   # Blue's effectiveness against Red
        
        # Model type
        self.model_type = tk.StringVar(value="cuadratico")
        
        # Fatigue parameters
        self.use_fatigue = tk.BooleanVar(value=False)
        self.fatigue_blue = tk.DoubleVar(value=0.001)
        self.fatigue_red = tk.DoubleVar(value=0.001)
        
        # Reinforcements
        self.use_reinforcements = tk.BooleanVar(value=False)
        self.reinf_blue_rate = tk.DoubleVar(value=1.0)
        self.reinf_blue_start = tk.DoubleVar(value=10.0)
        self.reinf_red_rate = tk.DoubleVar(value=0.8)
        self.reinf_red_start = tk.DoubleVar(value=15.0)
        
        # Economic parameters
        self.use_economics = tk.BooleanVar(value=False)
        self.budget_blue = tk.DoubleVar(value=10000.0)
        self.budget_red = tk.DoubleVar(value=8000.0)
        self.cost_soldier_blue = tk.DoubleVar(value=10.0)
        self.cost_soldier_red = tk.DoubleVar(value=8.0)
        self.cost_combat_blue = tk.DoubleVar(value=5.0)
        self.cost_combat_red = tk.DoubleVar(value=4.0)
        
        # Mercenary/Commerce model
        self.use_mercenaries = tk.BooleanVar(value=False)
        self.merc_cost_blue = tk.DoubleVar(value=20.0)
        self.merc_cost_red = tk.DoubleVar(value=18.0)
        self.merc_effectiveness = tk.DoubleVar(value=1.5)
        
        # Simulation parameters
        self.t_final = tk.DoubleVar(value=100.0)
        self.dt = tk.DoubleVar(value=0.1)
        
        # Results storage
        self.simulation_results = None
        self.economic_report = {}
        
        # Create UI
        self._create_ui()
        
    def _create_ui(self):
        """Create the main user interface."""
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (controls)
        left_frame = ttk.Frame(main_container, width=450)
        main_container.add(left_frame, weight=0)
        
        # Create scrollable left panel
        canvas_left = tk.Canvas(left_frame)
        scrollbar_left = ttk.Scrollbar(left_frame, orient="vertical", command=canvas_left.yview)
        self.scrollable_left = ttk.Frame(canvas_left)
        
        self.scrollable_left.bind(
            "<Configure>",
            lambda e: canvas_left.configure(scrollregion=canvas_left.bbox("all"))
        )
        
        canvas_left.create_window((0, 0), window=self.scrollable_left, anchor="nw")
        canvas_left.configure(yscrollcommand=scrollbar_left.set)
        
        scrollbar_left.pack(side=tk.RIGHT, fill=tk.Y)
        canvas_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Mousewheel scrolling
        canvas_left.bind_all("<MouseWheel>", lambda e: canvas_left.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Right panel (plots)
        self.right_panel = ttk.Frame(main_container)
        main_container.add(self.right_panel, weight=1)
        
        # Populate left panel
        self._create_initial_conditions()
        self._create_combat_parameters()
        self._create_model_selection()
        self._create_fatigue_section()
        self._create_reinforcements_section()
        self._create_economics_section()
        self._create_mercenary_section()
        self._create_simulation_parameters()
        self._create_control_buttons()
        self._create_results_display()
        
    def _create_initial_conditions(self):
        """Create initial conditions inputs."""
        frame = ttk.LabelFrame(self.scrollable_left, text="Condiciones Iniciales")
        frame.pack(fill=tk.X, padx=8, pady=4)
        
        ttk.Label(frame, text="Tropas Azules (Blue):").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(frame, textvariable=self.blue_initial, width=12).grid(row=0, column=1, padx=4, pady=2)
        
        ttk.Label(frame, text="Tropas Rojas (Red):").grid(row=1, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(frame, textvariable=self.red_initial, width=12).grid(row=1, column=1, padx=4, pady=2)
        
    def _create_combat_parameters(self):
        """Create combat effectiveness parameters."""
        frame = ttk.LabelFrame(self.scrollable_left, text="Parámetros de Combate")
        frame.pack(fill=tk.X, padx=8, pady=4)
        
        ttk.Label(frame, text="α (efectividad Red vs Blue):").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(frame, textvariable=self.alpha, width=12).grid(row=0, column=1, padx=4, pady=2)
        
        ttk.Label(frame, text="β (efectividad Blue vs Red):").grid(row=1, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(frame, textvariable=self.beta, width=12).grid(row=1, column=1, padx=4, pady=2)
        
    def _create_model_selection(self):
        """Create model type selection."""
        frame = ttk.LabelFrame(self.scrollable_left, text="Tipo de Modelo Lanchester")
        frame.pack(fill=tk.X, padx=8, pady=4)
        
        ttk.Radiobutton(frame, text="Lineal (guerrilla/antiguo)", 
                       variable=self.model_type, value="lineal").pack(anchor="w", padx=4, pady=2)
        ttk.Radiobutton(frame, text="Cuadrático (moderno/concentrado)", 
                       variable=self.model_type, value="cuadratico").pack(anchor="w", padx=4, pady=2)
        ttk.Radiobutton(frame, text="Mixto (Blue cuadrático, Red lineal)", 
                       variable=self.model_type, value="mixto").pack(anchor="w", padx=4, pady=2)
        
        help_text = ("Lineal: dB/dt = -αR, dR/dt = -βB\n"
                    "Cuadrático: dB/dt = -αR·R, dR/dt = -βB·B\n"
                    "Mixto: combina ambos")
        ttk.Label(frame, text=help_text, font=("Arial", 8), foreground="gray").pack(anchor="w", padx=4, pady=2)
        
    def _create_fatigue_section(self):
        """Create fatigue parameters."""
        frame = ttk.LabelFrame(self.scrollable_left, text="Fatiga/Desgaste")
        frame.pack(fill=tk.X, padx=8, pady=4)
        
        ttk.Checkbutton(frame, text="Incluir fatiga", variable=self.use_fatigue).pack(anchor="w", padx=4, pady=2)
        
        ttk.Label(frame, text="Tasa de fatiga Blue:").pack(anchor="w", padx=20, pady=2)
        ttk.Entry(frame, textvariable=self.fatigue_blue, width=12).pack(anchor="w", padx=20, pady=2)
        
        ttk.Label(frame, text="Tasa de fatiga Red:").pack(anchor="w", padx=20, pady=2)
        ttk.Entry(frame, textvariable=self.fatigue_red, width=12).pack(anchor="w", padx=20, pady=2)
        
    def _create_reinforcements_section(self):
        """Create reinforcements parameters."""
        frame = ttk.LabelFrame(self.scrollable_left, text="Refuerzos")
        frame.pack(fill=tk.X, padx=8, pady=4)
        
        ttk.Checkbutton(frame, text="Incluir refuerzos", variable=self.use_reinforcements).pack(anchor="w", padx=4, pady=2)
        
        ttk.Label(frame, text="Refuerzos Blue (tropas/tiempo):").pack(anchor="w", padx=20, pady=2)
        ttk.Entry(frame, textvariable=self.reinf_blue_rate, width=12).pack(anchor="w", padx=20, pady=2)
        
        ttk.Label(frame, text="Tiempo inicio refuerzos Blue:").pack(anchor="w", padx=20, pady=2)
        ttk.Entry(frame, textvariable=self.reinf_blue_start, width=12).pack(anchor="w", padx=20, pady=2)
        
        ttk.Label(frame, text="Refuerzos Red (tropas/tiempo):").pack(anchor="w", padx=20, pady=2)
        ttk.Entry(frame, textvariable=self.reinf_red_rate, width=12).pack(anchor="w", padx=20, pady=2)
        
        ttk.Label(frame, text="Tiempo inicio refuerzos Red:").pack(anchor="w", padx=20, pady=2)
        ttk.Entry(frame, textvariable=self.reinf_red_start, width=12).pack(anchor="w", padx=20, pady=2)
        
    def _create_economics_section(self):
        """Create economic parameters."""
        frame = ttk.LabelFrame(self.scrollable_left, text="Recursos Económicos")
        frame.pack(fill=tk.X, padx=8, pady=4)
        
        ttk.Checkbutton(frame, text="Incluir modelo económico", variable=self.use_economics).pack(anchor="w", padx=4, pady=2)
        
        ttk.Label(frame, text="Presupuesto Blue:").pack(anchor="w", padx=20, pady=2)
        ttk.Entry(frame, textvariable=self.budget_blue, width=12).pack(anchor="w", padx=20, pady=2)
        
        ttk.Label(frame, text="Presupuesto Red:").pack(anchor="w", padx=20, pady=2)
        ttk.Entry(frame, textvariable=self.budget_red, width=12).pack(anchor="w", padx=20, pady=2)
        
        ttk.Label(frame, text="Costo soldado Blue:").pack(anchor="w", padx=20, pady=2)
        ttk.Entry(frame, textvariable=self.cost_soldier_blue, width=12).pack(anchor="w", padx=20, pady=2)
        
        ttk.Label(frame, text="Costo soldado Red:").pack(anchor="w", padx=20, pady=2)
        ttk.Entry(frame, textvariable=self.cost_soldier_red, width=12).pack(anchor="w", padx=20, pady=2)
        
        ttk.Label(frame, text="Costo combate/tiempo Blue:").pack(anchor="w", padx=20, pady=2)
        ttk.Entry(frame, textvariable=self.cost_combat_blue, width=12).pack(anchor="w", padx=20, pady=2)
        
        ttk.Label(frame, text="Costo combate/tiempo Red:").pack(anchor="w", padx=20, pady=2)
        ttk.Entry(frame, textvariable=self.cost_combat_red, width=12).pack(anchor="w", padx=20, pady=2)
        
    def _create_mercenary_section(self):
        """Create mercenary/commerce parameters."""
        frame = ttk.LabelFrame(self.scrollable_left, text="Mercenarios/Comercio")
        frame.pack(fill=tk.X, padx=8, pady=4)
        
        ttk.Checkbutton(frame, text="Incluir mercenarios", variable=self.use_mercenaries).pack(anchor="w", padx=4, pady=2)
        
        ttk.Label(frame, text="Costo mercenario Blue:").pack(anchor="w", padx=20, pady=2)
        ttk.Entry(frame, textvariable=self.merc_cost_blue, width=12).pack(anchor="w", padx=20, pady=2)
        
        ttk.Label(frame, text="Costo mercenario Red:").pack(anchor="w", padx=20, pady=2)
        ttk.Entry(frame, textvariable=self.merc_cost_red, width=12).pack(anchor="w", padx=20, pady=2)
        
        ttk.Label(frame, text="Efectividad mercenarios (multiplicador):").pack(anchor="w", padx=20, pady=2)
        ttk.Entry(frame, textvariable=self.merc_effectiveness, width=12).pack(anchor="w", padx=20, pady=2)
        
    def _create_simulation_parameters(self):
        """Create simulation time parameters."""
        frame = ttk.LabelFrame(self.scrollable_left, text="Parámetros de Simulación")
        frame.pack(fill=tk.X, padx=8, pady=4)
        
        ttk.Label(frame, text="Tiempo final:").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(frame, textvariable=self.t_final, width=12).grid(row=0, column=1, padx=4, pady=2)
        
        ttk.Label(frame, text="Paso de tiempo (dt):").grid(row=1, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(frame, textvariable=self.dt, width=12).grid(row=1, column=1, padx=4, pady=2)
    
    def _create_quick_examples(self):
        """Create quick example buttons."""
        examples_frame = ttk.LabelFrame(self.scrollable_left, text="📚 Ejemplos Rápidos")
        examples_frame.pack(fill=tk.X, padx=8, pady=4)
        
        ttk.Label(examples_frame, text="Escenarios de Combate:", 
                 font=("Arial", 9, "bold")).pack(anchor="w", padx=4, pady=2)
        
        # Row 1: Warfare examples
        row1_frame = ttk.Frame(examples_frame)
        row1_frame.pack(fill=tk.X, padx=4, pady=2)
        
        tk.Button(row1_frame, text="Batalla Equilibrada", 
                  command=lambda: self._load_example1(),
                  bg="#16a085", fg='white',
                  activebackground="#1abc9c",
                  font=("Arial", 8, "bold"),
                  relief=tk.RAISED, bd=2, cursor='hand2',
                  width=15, height=2).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        tk.Button(row1_frame, text="Superioridad Blue", 
                  command=lambda: self._load_example2(),
                  bg="#16a085", fg='white',
                  activebackground="#1abc9c",
                  font=("Arial", 8, "bold"),
                  relief=tk.RAISED, bd=2, cursor='hand2',
                  width=15, height=2).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        tk.Button(row1_frame, text="Con Refuerzos", 
                  command=lambda: self._load_example3(),
                  bg="#16a085", fg='white',
                  activebackground="#1abc9c",
                  font=("Arial", 8, "bold"),
                  relief=tk.RAISED, bd=2, cursor='hand2',
                  width=15, height=2).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
    
    def _load_example1(self):
        """Batalla equilibrada - fuerzas y efectividad similares."""
        self.blue_initial.set(100)
        self.red_initial.set(100)
        self.alpha.set(0.01)  # Red efectividad contra Blue
        self.beta.set(0.01)   # Blue efectividad contra Red
        self.model_type.set("cuadratico")
        self.use_fatigue.set(False)
        self.use_reinforcements.set(False)
        self.use_economics.set(False)
        self.t_final.set(150)
        
    def _load_example2(self):
        """Superioridad Blue - más efectivo y más tropas."""
        self.blue_initial.set(120)
        self.red_initial.set(80)
        self.alpha.set(0.008)  # Red menos efectivo
        self.beta.set(0.015)   # Blue más efectivo
        self.model_type.set("cuadratico")
        self.use_fatigue.set(False)
        self.use_reinforcements.set(False)
        self.use_economics.set(False)
        self.t_final.set(100)
    
    def _load_example3(self):
        """Con refuerzos - Blue recibe apoyo constante."""
        self.blue_initial.set(80)
        self.red_initial.set(100)
        self.alpha.set(0.01)
        self.beta.set(0.01)
        self.model_type.set("cuadratico")
        self.use_fatigue.set(False)
        self.use_reinforcements.set(True)
        self.reinf_blue_rate.set(2.0)  # Blue recibe 2 tropas/unidad tiempo
        self.reinf_blue_start.set(20.0)
        self.reinf_red_rate.set(0.0)
        self.reinf_red_start.set(999.0)
        self.use_economics.set(False)
        self.t_final.set(150)
        
    def _create_control_buttons(self):
        """Create control buttons."""
        # Quick examples
        self._create_quick_examples()
        
        frame = ttk.LabelFrame(self.scrollable_left, text="Acciones")
        frame.pack(fill=tk.X, padx=8, pady=4)
        
        ttk.Button(frame, text="Simular", command=self.run_simulation).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(frame, text="Limpiar", command=self.clear_results).pack(fill=tk.X, padx=8, pady=4)
        
    def _create_results_display(self):
        """Create results display area."""
        frame = ttk.LabelFrame(self.scrollable_left, text="Resultados")
        frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        
        self.txt_results = ScrolledText(frame, wrap='word', font=("Consolas", 9), height=15)
        self.txt_results.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
    def run_simulation(self):
        """Run the Lanchester simulation."""
        try:
            # Clear previous results
            self.txt_results.delete(1.0, tk.END)
            
            # Get parameters
            B0 = self.blue_initial.get()
            R0 = self.red_initial.get()
            alpha = self.alpha.get()
            beta = self.beta.get()
            t_final = self.t_final.get()
            dt = self.dt.get()
            
            # Time array
            t = np.arange(0, t_final, dt)
            
            # Initial state
            if self.use_economics.get():
                y0 = [B0, R0, self.budget_blue.get(), self.budget_red.get()]
            else:
                y0 = [B0, R0]
            
            # Solve ODE
            solution = odeint(self._lanchester_equations, y0, t)
            
            # Store results
            self.simulation_results = {
                't': t,
                'Blue': solution[:, 0],
                'Red': solution[:, 1],
                'Budget_Blue': solution[:, 2] if self.use_economics.get() else None,
                'Budget_Red': solution[:, 3] if self.use_economics.get() else None
            }
            
            # Analyze results
            self._analyze_results()
            
            # Plot results
            self._plot_results()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la simulación:\n{str(e)}")
            
    def _lanchester_equations(self, y, t):
        """Define the Lanchester differential equations."""
        if self.use_economics.get():
            B, R, budget_B, budget_R = y
        else:
            B, R = y
            budget_B = budget_R = None
        
        alpha = self.alpha.get()
        beta = self.beta.get()
        model = self.model_type.get()
        
        # Base combat losses
        if model == "lineal":
            dB_combat = -alpha * R
            dR_combat = -beta * B
        elif model == "cuadratico":
            # Lanchester cuadrático: dB/dt = -α*R, dR/dt = -β*B (fuego concentrado)
            dB_combat = -alpha * R
            dR_combat = -beta * B
        elif model == "mixto":
            # Mixto: uno cuadrático, otro lineal
            dB_combat = -alpha * R
            dR_combat = -beta * B * R
        
        # Fatigue
        if self.use_fatigue.get():
            dB_combat -= self.fatigue_blue.get() * max(B, 0)
            dR_combat -= self.fatigue_red.get() * max(R, 0)
        
        # Reinforcements
        dB_reinf = 0
        dR_reinf = 0
        if self.use_reinforcements.get():
            if t >= self.reinf_blue_start.get():
                dB_reinf = self.reinf_blue_rate.get()
            if t >= self.reinf_red_start.get():
                dR_reinf = self.reinf_red_rate.get()
        
        # Apply economics constraints
        if self.use_economics.get():
            cost_B = max(B, 0) * self.cost_combat_blue.get() * self.dt.get()
            cost_R = max(R, 0) * self.cost_combat_red.get() * self.dt.get()
            
            # Add reinforcement costs
            if dB_reinf > 0:
                cost_B += dB_reinf * self.cost_soldier_blue.get() * self.dt.get()
            if dR_reinf > 0:
                cost_R += dR_reinf * self.cost_soldier_red.get() * self.dt.get()
            
            # Check budget
            if budget_B < cost_B:
                dB_reinf = 0
                dB_combat *= 0.5  # Reduced effectiveness with no budget
            
            if budget_R < cost_R:
                dR_reinf = 0
                dR_combat *= 0.5
            
            dBudget_B = -cost_B / self.dt.get()
            dBudget_R = -cost_R / self.dt.get()
        else:
            dBudget_B = dBudget_R = 0
        
        # Mercenaries
        if self.use_mercenaries.get() and self.use_economics.get():
            if budget_B > self.merc_cost_blue.get():
                merc_b = min(budget_B / self.merc_cost_blue.get(), 5) * self.dt.get()
                dB_reinf += merc_b * self.merc_effectiveness.get()
                dBudget_B -= merc_b * self.merc_cost_blue.get() / self.dt.get()
            
            if budget_R > self.merc_cost_red.get():
                merc_r = min(budget_R / self.merc_cost_red.get(), 5) * self.dt.get()
                dR_reinf += merc_r * self.merc_effectiveness.get()
                dBudget_R -= merc_r * self.merc_cost_red.get() / self.dt.get()
        
        dB = dB_combat + dB_reinf
        dR = dR_combat + dR_reinf
        
        if self.use_economics.get():
            return [dB, dR, dBudget_B, dBudget_R]
        else:
            return [dB, dR]
    
    def _analyze_results(self):
        """Analyze simulation results."""
        t = self.simulation_results['t']
        B = self.simulation_results['Blue']
        R = self.simulation_results['Red']
        
        self.txt_results.insert(tk.END, "═" * 60 + "\n")
        self.txt_results.insert(tk.END, "RESULTADOS DE LA SIMULACIÓN LANCHESTER\n")
        self.txt_results.insert(tk.END, "═" * 60 + "\n\n")
        
        # Model info
        self.txt_results.insert(tk.END, f"Modelo: {self.model_type.get().upper()}\n")
        self.txt_results.insert(tk.END, f"Tiempo simulado: 0 a {self.t_final.get()}\n\n")
        
        # Initial conditions
        self.txt_results.insert(tk.END, "CONDICIONES INICIALES:\n")
        self.txt_results.insert(tk.END, f"  Blue: {self.blue_initial.get():.1f} tropas\n")
        self.txt_results.insert(tk.END, f"  Red:  {self.red_initial.get():.1f} tropas\n")
        self.txt_results.insert(tk.END, f"  α (Red vs Blue): {self.alpha.get():.4f}\n")
        self.txt_results.insert(tk.END, f"  β (Blue vs Red): {self.beta.get():.4f}\n\n")
        
        # Find winner
        final_blue = B[-1]
        final_red = R[-1]
        
        self.txt_results.insert(tk.END, "RESULTADO FINAL:\n")
        self.txt_results.insert(tk.END, f"  Blue final: {final_blue:.2f} tropas\n")
        self.txt_results.insert(tk.END, f"  Red final:  {final_red:.2f} tropas\n")
        
        if final_blue > 1 and final_red < 1:
            winner = "BLUE"
            self.txt_results.insert(tk.END, f"\n✓ GANADOR: {winner}\n")
            self.txt_results.insert(tk.END, f"  Tropas sobrevivientes: {final_blue:.2f}\n")
        elif final_red > 1 and final_blue < 1:
            winner = "RED"
            self.txt_results.insert(tk.END, f"\n✓ GANADOR: {winner}\n")
            self.txt_results.insert(tk.END, f"  Tropas sobrevivientes: {final_red:.2f}\n")
        else:
            winner = "EMPATE"
            self.txt_results.insert(tk.END, f"\n⚖ RESULTADO: {winner}\n")
            self.txt_results.insert(tk.END, f"  Ambos bandos destruidos o muy debilitados\n")
        
        # Time to conclusion
        threshold = 1.0
        blue_eliminated = np.where(B < threshold)[0]
        red_eliminated = np.where(R < threshold)[0]
        
        if len(blue_eliminated) > 0:
            t_blue_elim = t[blue_eliminated[0]]
            self.txt_results.insert(tk.END, f"\n  Blue eliminado en t = {t_blue_elim:.2f}\n")
        
        if len(red_eliminated) > 0:
            t_red_elim = t[red_eliminated[0]]
            self.txt_results.insert(tk.END, f"  Red eliminado en t = {t_red_elim:.2f}\n")
        
        # Losses
        blue_losses = self.blue_initial.get() - max(final_blue, 0)
        red_losses = self.red_initial.get() - max(final_red, 0)
        
        self.txt_results.insert(tk.END, f"\nPÉRDIDAS:\n")
        self.txt_results.insert(tk.END, f"  Blue: {blue_losses:.2f} ({100*blue_losses/self.blue_initial.get():.1f}%)\n")
        self.txt_results.insert(tk.END, f"  Red:  {red_losses:.2f} ({100*red_losses/self.red_initial.get():.1f}%)\n")
        
        # Economic analysis
        if self.use_economics.get():
            budget_B = self.simulation_results['Budget_Blue']
            budget_R = self.simulation_results['Budget_Red']
            
            self.txt_results.insert(tk.END, f"\nANÁLISIS ECONÓMICO:\n")
            self.txt_results.insert(tk.END, f"  Presupuesto inicial Blue: ${self.budget_blue.get():.2f}\n")
            self.txt_results.insert(tk.END, f"  Presupuesto final Blue:   ${max(budget_B[-1], 0):.2f}\n")
            self.txt_results.insert(tk.END, f"  Gasto total Blue:         ${self.budget_blue.get() - max(budget_B[-1], 0):.2f}\n\n")
            
            self.txt_results.insert(tk.END, f"  Presupuesto inicial Red:  ${self.budget_red.get():.2f}\n")
            self.txt_results.insert(tk.END, f"  Presupuesto final Red:    ${max(budget_R[-1], 0):.2f}\n")
            self.txt_results.insert(tk.END, f"  Gasto total Red:          ${self.budget_red.get() - max(budget_R[-1], 0):.2f}\n")
            
            # Cost per casualty
            if blue_losses > 0:
                cost_per_red_casualty = (self.budget_blue.get() - max(budget_B[-1], 0)) / blue_losses
                self.txt_results.insert(tk.END, f"\n  Costo por baja Blue: ${cost_per_red_casualty:.2f}\n")
            
            if red_losses > 0:
                cost_per_blue_casualty = (self.budget_red.get() - max(budget_R[-1], 0)) / red_losses
                self.txt_results.insert(tk.END, f"  Costo por baja Red:  ${cost_per_blue_casualty:.2f}\n")
        
        # Predictions based on Lanchester laws
        self.txt_results.insert(tk.END, f"\n{'─' * 60}\n")
        self.txt_results.insert(tk.END, "ANÁLISIS TEÓRICO:\n")
        
        if self.model_type.get() == "cuadratico":
            # Lanchester square law prediction
            N_blue = self.blue_initial.get()
            N_red = self.red_initial.get()
            
            lanchester_coef_blue = self.beta.get() * N_blue**2
            lanchester_coef_red = self.alpha.get() * N_red**2
            
            self.txt_results.insert(tk.END, f"Ley Cuadrática de Lanchester:\n")
            self.txt_results.insert(tk.END, f"  β·B₀² = {lanchester_coef_blue:.2f}\n")
            self.txt_results.insert(tk.END, f"  α·R₀² = {lanchester_coef_red:.2f}\n")
            
            if lanchester_coef_blue > lanchester_coef_red:
                predicted_winner = "Blue"
                remaining = np.sqrt(lanchester_coef_blue - lanchester_coef_red) / np.sqrt(self.beta.get())
            elif lanchester_coef_red > lanchester_coef_blue:
                predicted_winner = "Red"
                remaining = np.sqrt(lanchester_coef_red - lanchester_coef_blue) / np.sqrt(self.alpha.get())
            else:
                predicted_winner = "Empate"
                remaining = 0
            
            self.txt_results.insert(tk.END, f"\n  Predicción teórica: {predicted_winner} gana\n")
            if predicted_winner != "Empate":
                self.txt_results.insert(tk.END, f"  Tropas restantes (teórico): {remaining:.2f}\n")
        
        self.txt_results.insert(tk.END, f"\n{'═' * 60}\n")
        
    def _plot_results(self):
        """Plot simulation results."""
        # Clear previous plots
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        
        t = self.simulation_results['t']
        B = self.simulation_results['Blue']
        R = self.simulation_results['Red']
        
        if self.use_economics.get():
            fig = Figure(figsize=(12, 10))
            
            # Troops over time
            ax1 = fig.add_subplot(221)
            ax1.plot(t, B, 'b-', linewidth=2, label='Blue')
            ax1.plot(t, R, 'r-', linewidth=2, label='Red')
            ax1.set_xlabel('Tiempo', fontsize=11)
            ax1.set_ylabel('Tropas', fontsize=11)
            ax1.set_title('Evolución de Tropas', fontsize=12, fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim(bottom=0)
            
            # Budget over time
            ax2 = fig.add_subplot(222)
            budget_B = self.simulation_results['Budget_Blue']
            budget_R = self.simulation_results['Budget_Red']
            ax2.plot(t, budget_B, 'b--', linewidth=2, label='Presupuesto Blue')
            ax2.plot(t, budget_R, 'r--', linewidth=2, label='Presupuesto Red')
            ax2.set_xlabel('Tiempo', fontsize=11)
            ax2.set_ylabel('Presupuesto ($)', fontsize=11)
            ax2.set_title('Recursos Económicos', fontsize=12, fontweight='bold')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.set_ylim(bottom=0)
            
            # Phase portrait
            ax3 = fig.add_subplot(223)
            ax3.plot(B, R, 'g-', linewidth=2)
            ax3.plot(B[0], R[0], 'go', markersize=10, label='Inicio')
            ax3.plot(B[-1], R[-1], 'rx', markersize=10, label='Final')
            ax3.set_xlabel('Blue', fontsize=11)
            ax3.set_ylabel('Red', fontsize=11)
            ax3.set_title('Espacio de Fases', fontsize=12, fontweight='bold')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # Losses over time
            ax4 = fig.add_subplot(224)
            B_losses = self.blue_initial.get() - B
            R_losses = self.red_initial.get() - R
            ax4.plot(t, B_losses, 'b-', linewidth=2, label='Bajas Blue')
            ax4.plot(t, R_losses, 'r-', linewidth=2, label='Bajas Red')
            ax4.set_xlabel('Tiempo', fontsize=11)
            ax4.set_ylabel('Bajas Acumuladas', fontsize=11)
            ax4.set_title('Pérdidas en Combate', fontsize=12, fontweight='bold')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            
        else:
            fig = Figure(figsize=(12, 8))
            
            # Troops over time
            ax1 = fig.add_subplot(211)
            ax1.plot(t, B, 'b-', linewidth=2, label='Blue')
            ax1.plot(t, R, 'r-', linewidth=2, label='Red')
            ax1.set_xlabel('Tiempo', fontsize=11)
            ax1.set_ylabel('Tropas', fontsize=11)
            ax1.set_title('Evolución de Tropas en el Tiempo', fontsize=12, fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim(bottom=0)
            
            # Phase portrait
            ax2 = fig.add_subplot(212)
            ax2.plot(B, R, 'g-', linewidth=2)
            ax2.plot(B[0], R[0], 'go', markersize=10, label='Inicio')
            ax2.plot(B[-1], R[-1], 'rx', markersize=10, label='Final')
            ax2.set_xlabel('Tropas Blue', fontsize=11)
            ax2.set_ylabel('Tropas Red', fontsize=11)
            ax2.set_title('Espacio de Fases (Blue vs Red)', fontsize=12, fontweight='bold')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        fig.tight_layout()
        
        # Add canvas
        canvas = FigureCanvasTkAgg(fig, master=self.right_panel)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def clear_results(self):
        """Clear all results."""
        self.txt_results.delete(1.0, tk.END)
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        self.simulation_results = None


def main():
    root = tk.Tk()
    app = LanchesterSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
