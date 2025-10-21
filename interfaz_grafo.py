import tkinter as tk
from tkinter import filedialog, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
from grafo_aereopuertos import GrafoAeropuertos


class InterfazGrafo:
    def __init__(self, root, grafo=None):
        self.root = root
        self.root.title("Sistema de Aeropuertos ✈️")
        self.root.geometry("1366x768")
        self.root.configure(bg="#f0f4f7")

        self.grafo = grafo if grafo else GrafoAeropuertos()
        self.ruta_csv = None
        self.zoom_scale = 1.0

        sys.stdout = self

        # --- FRAME BOTONES ---
        frame_botones = tk.Frame(self.root, bg="#e0e6eb", pady=10)
        frame_botones.pack(fill=tk.X)

        tk.Button(frame_botones, text="Cargar CSV", command=self.cargar_csv,
                  width=15, bg="#4A90E2", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botones, text="Verificar Conexidad", command=self.verificar_conexidad,
                  width=20, bg="#4A90E2", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botones, text="Árbol Exp. Mínima", command=self.mst,
                  width=20, bg="#4A90E2", fg="white").pack(side=tk.LEFT, padx=5)

        self.entry_origen = tk.Entry(frame_botones, width=8)
        self.entry_origen.pack(side=tk.LEFT, padx=5)
        self.entry_destino = tk.Entry(frame_botones, width=8)
        self.entry_destino.pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botones, text="Camino mínimo", command=self.camino_minimo,
                  width=15, bg="#50C878", fg="white").pack(side=tk.LEFT, padx=5)

        self.entry_codigo = tk.Entry(frame_botones, width=8)
        self.entry_codigo.pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botones, text="Top 10 más lejanos", command=self.mas_lejanos,
                  width=18, bg="#50C878", fg="white").pack(side=tk.LEFT, padx=5)

        # --- FRAME GRAFO ---
        frame_grafo = tk.Frame(self.root, bg="white")
        frame_grafo.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.ax.set_axis_off()
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_grafo)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.mpl_connect("scroll_event", self.on_zoom)

        # --- FRAME SALIDA ---
        frame_salida = tk.Frame(self.root)
        frame_salida.pack(fill=tk.BOTH, padx=10, pady=10)
        tk.Label(frame_salida, text="Salida de información:", bg="#f0f4f7").pack(anchor="w")
        self.text_salida = tk.Text(frame_salida, height=10, wrap=tk.WORD, bg="#f7f9fa")
        self.text_salida.pack(fill=tk.BOTH, expand=True)
        self.text_salida.insert(tk.END, "Bienvenido al sistema de aeropuertos.\n")

        # Si el grafo ya tiene datos, mostrarlo
        if self.grafo.grafo:
            self.root.after(500, self.mostrar_grafo)

    # --------------------------------------------------
    def write(self, texto):
        try:
            if self.text_salida.winfo_exists():
                self.text_salida.insert(tk.END, texto)
                self.text_salida.see(tk.END)
            sys.__stdout__.write(texto)
        except tk.TclError:
            pass

    def flush(self):
        pass

    # --------------------------------------------------
    def cargar_csv(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo CSV", filetypes=[("Archivos CSV", "*.csv")])
        if not ruta:
            return
        self.ruta_csv = ruta
        print(f"\nArchivo seleccionado: {ruta}")
        if self.grafo.cargar_datos(ruta):
            messagebox.showinfo("Éxito", "Archivo CSV cargado correctamente.")
            self.root.after(100, self.mostrar_grafo)  # evitar freeze
        else:
            messagebox.showerror("Error", "No se pudo cargar el archivo CSV.")

    def mostrar_grafo(self, subgrafo=None, color_aristas="#888", color_nodos="#4A90E2"):
        self.ax.clear()
        self.ax.set_axis_off()

        G = nx.Graph()
        datos = subgrafo if subgrafo else self.grafo.grafo

        for origen, vecinos in datos.items():
            for destino, peso in vecinos.items():
                G.add_edge(origen, destino, weight=peso)

        # Layout más rápido y espacioso
        pos = nx.fruchterman_reingold_layout(G, iterations=30)
        nx.draw_networkx_nodes(G, pos, node_size=100, node_color=color_nodos, alpha=0.85, ax=self.ax)
        nx.draw_networkx_edges(G, pos, width=1.0, edge_color=color_aristas, alpha=0.6, ax=self.ax)
        nx.draw_networkx_labels(G, pos, font_size=6, ax=self.ax)

        self.canvas.draw()

    def verificar_conexidad(self):
        es_conexo, componentes = self.grafo.es_conexo()
        print("\n--- CONEXIDAD DEL GRAFO ---")
        print(f"¿Es conexo? {'Sí' if es_conexo else 'No'}")
        print(f"Componentes: {len(componentes)}")
        for i, comp in enumerate(componentes, 1):
            print(f"  Componente {i}: {len(comp)} vértices\n")
        self.mostrar_grafo()

    def mst(self):
        _, componentes = self.grafo.es_conexo()
        print("\n--- ÁRBOL DE EXPANSIÓN MÍNIMA ---")
        for i, comp in enumerate(componentes, 1):
            peso, aristas = self.grafo.prim_mst(comp)
            print(f"Componente {i} - Peso total: {peso:.2f} km, Aristas: {len(aristas)}")
        print()

        if componentes:
            peso, aristas = self.grafo.prim_mst(componentes[0])
            subgrafo = {}
            for u, v, w in aristas:
                subgrafo.setdefault(u, {})[v] = w
                subgrafo.setdefault(v, {})[u] = w
            self.mostrar_grafo(subgrafo, color_aristas="#50C878", color_nodos="#E87461")

    def mas_lejanos(self):
        codigo = self.entry_codigo.get().strip().upper()
        if not codigo:
            messagebox.showwarning("Atención", "Ingrese un código de aeropuerto.")
            return
        print(f"\n--- 10 AEROPUERTOS MÁS LEJANOS DESDE {codigo} ---")
        self.grafo.aeropuertos_mas_lejanos(codigo)

    def camino_minimo(self):
        origen = self.entry_origen.get().strip().upper()
        destino = self.entry_destino.get().strip().upper()
        if not origen or not destino:
            messagebox.showwarning("Atención", "Ingrese ambos aeropuertos.")
            return

        distancias, predecesores = self.grafo.dijkstra(origen)
        if distancias.get(destino, float('inf')) == float('inf'):
            messagebox.showerror("Sin conexión", f"No hay camino entre {origen} y {destino}.")
            return

        camino = []
        actual = destino
        while actual:
            camino.append(actual)
            actual = predecesores[actual]
        camino.reverse()

        print(f"\n--- CAMINO MÍNIMO {origen} → {destino} ---")
        print(f"Ruta: {' → '.join(camino)}")
        print(f"Distancia total: {distancias[destino]:.2f} km\n")

        subgrafo = {}
        for i in range(len(camino) - 1):
            u, v = camino[i], camino[i + 1]
            w = self.grafo.grafo[u][v]
            subgrafo.setdefault(u, {})[v] = w
            subgrafo.setdefault(v, {})[u] = w
        self.mostrar_grafo(subgrafo, color_aristas="#E74C3C", color_nodos="#F4D03F")

    # --------------------------------------------------
    def on_zoom(self, event):
        base_scale = 1.2
        if event.button == 'up':
            self.zoom_scale *= base_scale
        elif event.button == 'down':
            self.zoom_scale /= base_scale
        self.zoom_scale = max(0.1, min(self.zoom_scale, 5.0))

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.ax.set_xlim([x * self.zoom_scale for x in xlim])
        self.ax.set_ylim([y * self.zoom_scale for y in ylim])
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazGrafo(root)
    root.mainloop()
