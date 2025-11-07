#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Dynamical Systems Simulation Suite
==========================================
A comprehensive collection of dynamical systems analysis tools combined in a 
user-friendly interface.

Modules:
- 1D Bifurcation Analysis
- 2D Linear Systems
- 2D Nonlinear Systems
- Lanchester Warfare Models
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
import sys

# Import all simulation modules
from bifurcaciones_1 import BifurcationApp
from sistemas_lineales_2d import LinearSystem2DApp
from sistemas_no_lineales_2d import NonlinearSystem2DApp
from simulador_lanchester import LanchesterSimulator


class SimulationLauncher(tk.Tk):
    """
    Main launcher window for the unified simulation suite.
    Provides a clean, minimalistic interface for selecting different analysis tools.
    """
    
    def __init__(self):
        super().__init__()
        
        self.title("Simulaciones de Sistemas Dinámicos")
        self.geometry("900x650")
        self.configure(bg='#f0f0f0')
        
        # Make window appear in center of screen
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        self._setup_styles()
        self._create_ui()
        
    def _setup_styles(self):
        """Configure custom styles for a modern, clean look"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom colors
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#34495e',
            'accent': '#3498db',
            'success': '#27ae60',
            'background': '#ecf0f1',
            'card': '#ffffff',
            'text': '#2c3e50',
            'text_light': '#7f8c8d'
        }
        
        # Configure button style
        style.configure('Card.TFrame',
                       background=self.colors['card'],
                       relief='flat')
        
    def _create_ui(self):
        """Create the main user interface"""
        # Main container with padding
        main_frame = tk.Frame(self, bg=self.colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Header
        self._create_header(main_frame)
        
        # Simulation cards container
        cards_frame = tk.Frame(main_frame, bg=self.colors['background'])
        cards_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Create 2x2 grid of simulation cards
        self._create_simulation_cards(cards_frame)
        
        # Footer
        self._create_footer(main_frame)
        
    def _create_header(self, parent):
        """Create the header section with title and subtitle"""
        header_frame = tk.Frame(parent, bg=self.colors['background'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Main title
        title_font = tkfont.Font(family="Segoe UI", size=28, weight="bold")
        title = tk.Label(
            header_frame,
            text="Simulaciones de Sistemas Dinámicos",
            font=title_font,
            fg=self.colors['primary'],
            bg=self.colors['background']
        )
        title.pack()
        
        # Subtitle
        subtitle_font = tkfont.Font(family="Segoe UI", size=11)
        subtitle = tk.Label(
            header_frame,
            text="Seleccione el tipo de análisis que desea realizar",
            font=subtitle_font,
            fg=self.colors['text_light'],
            bg=self.colors['background']
        )
        subtitle.pack(pady=(5, 0))
        
    def _create_simulation_cards(self, parent):
        """Create the grid of simulation option cards"""
        
        # Simulation configurations
        simulations = [
            {
                'title': 'Bifurcaciones 1D',
                'dimension': '1 Dimensión',
                'description': 'Análisis de bifurcaciones en sistemas unidimensionales',
                'details': '• Diagramas de bifurcación\n• Detección automática de tipos\n• Análisis de estabilidad\n• Retratos de fase',
                'color': '#e74c3c',
                'command': self._launch_bifurcations
            },
            {
                'title': 'Sistemas Lineales',
                'dimension': '2 Dimensiones',
                'description': 'Análisis de sistemas dinámicos lineales 2D',
                'details': '• Retratos de fase\n• Clasificación de puntos críticos\n• Mapas de Poincaré\n• Entrada por matriz o ecuaciones',
                'color': '#3498db',
                'command': self._launch_linear_systems
            },
            {
                'title': 'Sistemas No Lineales',
                'dimension': '2 Dimensiones',
                'description': 'Análisis de sistemas dinámicos no lineales 2D',
                'details': '• Puntos de equilibrio\n• Linearización (Jacobiano)\n• Clasificación hiperbólica\n• Sistemas conservativos',
                'color': '#9b59b6',
                'command': self._launch_nonlinear_systems
            },
            {
                'title': 'Lanchester',
                'dimension': 'Modelos de Combate',
                'description': 'Simulación de modelos de guerra de Lanchester',
                'details': '• Modelos lineal/cuadrático/mixto\n• Análisis económico\n• Refuerzos y fatiga\n• Mercenarios',
                'color': '#16a085',
                'command': self._launch_lanchester
            }
        ]
        
        # Create 2x2 grid
        for i, sim in enumerate(simulations):
            row = i // 2
            col = i % 2
            
            card = self._create_card(parent, sim)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
        # Configure grid weights for equal distribution
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        
    def _create_card(self, parent, config):
        """Create a single simulation card"""
        # Card frame with shadow effect
        card_frame = tk.Frame(parent, bg=self.colors['card'], relief='raised', bd=1)
        
        # Color strip at top
        color_strip = tk.Frame(card_frame, bg=config['color'], height=6)
        color_strip.pack(fill=tk.X)
        
        # Card content
        content = tk.Frame(card_frame, bg=self.colors['card'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Title
        title_font = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        title = tk.Label(
            content,
            text=config['title'],
            font=title_font,
            fg=self.colors['primary'],
            bg=self.colors['card']
        )
        title.pack(anchor='w')
        
        # Dimension badge
        badge_frame = tk.Frame(content, bg=config['color'], bd=0)
        badge_frame.pack(anchor='w', pady=(5, 10))
        
        dimension_font = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        dimension = tk.Label(
            badge_frame,
            text=config['dimension'],
            font=dimension_font,
            fg='white',
            bg=config['color'],
            padx=8,
            pady=2
        )
        dimension.pack()
        
        # Description
        desc_font = tkfont.Font(family="Segoe UI", size=10)
        description = tk.Label(
            content,
            text=config['description'],
            font=desc_font,
            fg=self.colors['text'],
            bg=self.colors['card'],
            wraplength=350,
            justify='left'
        )
        description.pack(anchor='w', pady=(0, 10))
        
        # Details
        details_font = tkfont.Font(family="Segoe UI", size=9)
        details = tk.Label(
            content,
            text=config['details'],
            font=details_font,
            fg=self.colors['text_light'],
            bg=self.colors['card'],
            justify='left'
        )
        details.pack(anchor='w', pady=(0, 15))
        
        # Launch button
        button_frame = tk.Frame(content, bg=self.colors['card'])
        button_frame.pack(fill=tk.X)
        
        launch_btn = tk.Button(
            button_frame,
            text="Abrir Simulación",
            command=config['command'],
            bg=config['color'],
            fg='white',
            font=tkfont.Font(family="Segoe UI", size=10, weight="bold"),
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8
        )
        launch_btn.pack(fill=tk.X)
        
        # Hover effects
        def on_enter(e):
            launch_btn.config(bg=self._darken_color(config['color']))
            
        def on_leave(e):
            launch_btn.config(bg=config['color'])
            
        launch_btn.bind('<Enter>', on_enter)
        launch_btn.bind('<Leave>', on_leave)
        
        return card_frame
    
    def _darken_color(self, hex_color):
        """Darken a hex color by 20% for hover effect"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = int(r * 0.8)
        g = int(g * 0.8)
        b = int(b * 0.8)
        return f'#{r:02x}{g:02x}{b:02x}'
        
    def _create_footer(self, parent):
        """Create the footer section"""
        footer_frame = tk.Frame(parent, bg=self.colors['background'])
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Info text
        info_font = tkfont.Font(family="Segoe UI", size=9)
        info = tk.Label(
            footer_frame,
            text="Modelado y Simulación - UADE | Todas las simulaciones mantienen su funcionalidad completa",
            font=info_font,
            fg=self.colors['text_light'],
            bg=self.colors['background']
        )
        info.pack()
        
    # Launch methods for each simulation
    def _launch_bifurcations(self):
        """Launch the 1D Bifurcation Analysis tool"""
        self.iconify()  # Minimize launcher
        try:
            app = BifurcationApp()
            app.protocol("WM_DELETE_WINDOW", lambda: self._on_simulation_close(app))
            app.mainloop()
        except Exception as e:
            self._show_error("Bifurcaciones 1D", str(e))
            self.deiconify()
    
    def _launch_linear_systems(self):
        """Launch the 2D Linear Systems tool"""
        self.iconify()
        try:
            app = LinearSystem2DApp()
            app.protocol("WM_DELETE_WINDOW", lambda: self._on_simulation_close(app))
            app.mainloop()
        except Exception as e:
            self._show_error("Sistemas Lineales 2D", str(e))
            self.deiconify()
    
    def _launch_nonlinear_systems(self):
        """Launch the 2D Nonlinear Systems tool"""
        self.iconify()
        try:
            root = tk.Toplevel()
            app = NonlinearSystem2DApp(root)
            root.protocol("WM_DELETE_WINDOW", lambda: self._on_simulation_close(root))
            root.mainloop()
        except Exception as e:
            self._show_error("Sistemas No Lineales 2D", str(e))
            self.deiconify()
    
    def _launch_lanchester(self):
        """Launch the Lanchester Warfare Simulator"""
        self.iconify()
        try:
            root = tk.Toplevel()
            app = LanchesterSimulator(root)
            root.protocol("WM_DELETE_WINDOW", lambda: self._on_simulation_close(root))
            root.mainloop()
        except Exception as e:
            self._show_error("Simulador Lanchester", str(e))
            self.deiconify()
    
    def _on_simulation_close(self, window):
        """Handle simulation window closure and restore launcher"""
        window.destroy()
        self.deiconify()
        self.lift()
        self.focus_force()
    
    def _show_error(self, simulation_name, error_msg):
        """Display error message if simulation fails to launch"""
        from tkinter import messagebox
        messagebox.showerror(
            "Error al Abrir Simulación",
            f"No se pudo abrir {simulation_name}:\n\n{error_msg}"
        )


def main():
    """Main entry point for the unified simulation suite"""
    try:
        app = SimulationLauncher()
        app.mainloop()
    except Exception as e:
        print(f"Error crítico: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
