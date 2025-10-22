import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.collections import LineCollection
import matplotlib.image as mpimg
import os, sys, urllib.request
from grafo_aereopuertos import GrafoAeropuertos


class InterfazGrafo:
    def __init__(self, root, grafo=None, fullscreen=True):
        self.root = root
        self.root.title("Sistema de Aeropuertos ✈️")
        self.root.configure(bg="#f0f4f7")

        if fullscreen:
            try:
                self.root.attributes("-fullscreen", True)
            except Exception:
                self.root.state("zoomed")
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self.grafo = grafo if grafo else GrafoAeropuertos()
        self.zoom_scale = 1.0
        self.zoom_step = 1.05
        self.pan_x = 0
        self.pan_y = 0
        self.ruta_csv = None

        # Guardar el subgrafo actual
        self._subgrafo_actual = None
        self._color_aristas = "#444"
        self._color_nodos = "#007ACC"

        sys.stdout = self

        # ===== FRAME SUPERIOR =====
        frame_botones = tk.Frame(self.root, bg="#e0e6eb", pady=8)
        frame_botones.pack(fill=tk.X)

        tk.Button(frame_botones, text="Cargar CSV", command=self.cargar_csv,
                  width=14, bg="#4A90E2", fg="white").pack(side=tk.LEFT, padx=6)
        tk.Button(frame_botones, text="Verificar Conexidad", command=self.verificar_conexidad,
                  width=18, bg="#4A90E2", fg="white").pack(side=tk.LEFT, padx=6)
        tk.Button(frame_botones, text="Árbol Exp. Mínima", command=self.mst,
                  width=16, bg="#4A90E2", fg="white").pack(side=tk.LEFT, padx=6)

        tk.Label(frame_botones, text="Origen:", bg="#e0e6eb").pack(side=tk.LEFT, padx=(12, 2))
        self.entry_origen = tk.Entry(frame_botones, width=8)
        self.entry_origen.pack(side=tk.LEFT, padx=4)
        tk.Label(frame_botones, text="Destino:", bg="#e0e6eb").pack(side=tk.LEFT, padx=(8, 2))
        self.entry_destino = tk.Entry(frame_botones, width=8)
        self.entry_destino.pack(side=tk.LEFT, padx=4)
        tk.Button(frame_botones, text="Camino mínimo", command=self.camino_minimo,
                  width=14, bg="#50C878", fg="white").pack(side=tk.LEFT, padx=6)

        tk.Label(frame_botones, text="Código:", bg="#e0e6eb").pack(side=tk.LEFT, padx=(12, 2))
        self.entry_codigo = tk.Entry(frame_botones, width=8)
        self.entry_codigo.pack(side=tk.LEFT, padx=4)
        tk.Button(frame_botones, text="Top 10 más lejanos", command=self.mas_lejanos,
                  width=16, bg="#50C878", fg="white").pack(side=tk.LEFT, padx=6)

        instr = "Zoom: W/S | Mover: ← ↑ ↓ → | Esc: salir fullscreen"
        tk.Label(frame_botones, text=instr, bg="#e0e6eb", fg="#333").pack(side=tk.RIGHT, padx=10)

        # Eventos de teclado
        self.root.bind("w", lambda e: self._zoom_key(True))
        self.root.bind("s", lambda e: self._zoom_key(False))
        self.root.bind("<Up>", lambda e: self._move_view(0, 10))
        self.root.bind("<Down>", lambda e: self._move_view(0, -10))
        self.root.bind("<Left>", lambda e: self._move_view(-10, 0))
        self.root.bind("<Right>", lambda e: self._move_view(10, 0))

        # ===== FRAME CENTRAL =====
        frame_grafo = tk.Frame(self.root, bg="white")
        frame_grafo.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.fig, self.ax = plt.subplots(figsize=(14, 6))
        self.ax.set_axis_off()
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_grafo)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.mapa = self._cargar_mapa_fondo()
        if self.mapa is not None:
            self.ax.imshow(self.mapa, extent=[-180, 180, -90, 90], zorder=0)
        else:
            self.ax.set_facecolor("#E0E0E0")

        # ===== FRAME INFERIOR =====
        frame_salida = tk.Frame(self.root)
        frame_salida.pack(fill=tk.BOTH, padx=10, pady=8)
        tk.Label(frame_salida, text="Salida de información:", bg="#f0f4f7").pack(anchor="w")
        self.text_salida = tk.Text(frame_salida, height=9, wrap=tk.WORD, bg="#f7f9fa")
        self.text_salida.pack(fill=tk.BOTH, expand=True)
        self.text_salida.insert(tk.END, "Bienvenido al sistema de aeropuertos.\n")

        if self.grafo.grafo:
            self.root.after(300, self.mostrar_grafo)

    # ===== AUX =====
    def _cargar_mapa_fondo(self):
        archivo = "world_map.jpg"
        if os.path.exists(archivo):
            try:
                return mpimg.imread(archivo)
            except Exception:
                return None
        else:
            print("Descargando mapa mundial...")
            url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/World_map_-_low_resolution.svg/2048px-World_map_-_low_resolution.svg.png"
            try:
                urllib.request.urlretrieve(url, archivo)
                return mpimg.imread(archivo)
            except Exception as e:
                print("⚠️ No se pudo descargar el mapa:", e)
                return None

    def write(self, texto):
        try:
            self.text_salida.insert(tk.END, texto)
            self.text_salida.see(tk.END)
            sys.__stdout__.write(texto)
        except Exception:
            pass

    def flush(self): pass

    # ===== FUNCIONES =====
    def cargar_csv(self):
        ruta = filedialog.askopenfilename(title="Seleccionar CSV", filetypes=[("CSV files", "*.csv")])
        if not ruta:
            return
        self.ruta_csv = ruta
        print(f"\nArchivo seleccionado: {ruta}")
        if self.grafo.cargar_datos(ruta):
            messagebox.showinfo("Éxito", "Archivo CSV cargado correctamente.")
            self.root.after(200, self.mostrar_grafo)
        else:
            messagebox.showerror("Error", "Error al cargar el CSV.")

    def _get_positions(self, subgrafo=None):
        datos = subgrafo if subgrafo else self.grafo.grafo
        pos = {}
        for code in datos:
            info = self.grafo.aeropuertos.get(code)
            if info:
                try:
                    lon = float(info["longitud"])
                    lat = float(info["latitud"])
                    pos[code] = (lon, lat)
                except:
                    continue
        for v in datos.values():
            for code in v:
                if code not in pos:
                    info = self.grafo.aeropuertos.get(code)
                    if info:
                        try:
                            lon = float(info["longitud"])
                            lat = float(info["latitud"])
                            pos[code] = (lon, lat)
                        except:
                            continue
        return pos

    def mostrar_grafo(self, subgrafo=None, color_aristas="#444", color_nodos="#007ACC"):
        self._subgrafo_actual = subgrafo
        self._color_aristas = color_aristas
        self._color_nodos = color_nodos

        self.ax.clear()
        if self.mapa is not None:
            self.ax.imshow(self.mapa, extent=[-180, 180, -90, 90], zorder=0)
        else:
            self.ax.set_facecolor("#E0E0E0")

        # límites ajustados con zoom y desplazamiento
        x_min, x_max = (-180 / self.zoom_scale) + self.pan_x, (180 / self.zoom_scale) + self.pan_x
        y_min, y_max = (-90 / self.zoom_scale) + self.pan_y, (90 / self.zoom_scale) + self.pan_y
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.ax.set_axis_off()

        datos = subgrafo if subgrafo else self.grafo.grafo
        pos = self._get_positions(datos)

        segmentos = []
        for u, vecinos in datos.items():
            for v, w in vecinos.items():
                if u in pos and v in pos:
                    segmentos.append([pos[u], pos[v]])
        if segmentos:
            lc = LineCollection(segmentos, linewidths=0.4, colors=color_aristas, alpha=0.5, zorder=2)
            self.ax.add_collection(lc)

        xs = [v[0] for v in pos.values()]
        ys = [v[1] for v in pos.values()]
        self.ax.scatter(xs, ys, s=15, c=color_nodos, alpha=0.8, zorder=3)

        # Mostrar etiquetas según zoom
        if len(pos) < 200 or self.zoom_scale > 1.8:
            for code, (x, y) in pos.items():
                nombre = self.grafo.aeropuertos.get(code, {}).get("nombre", "")
                self.ax.text(x, y, f"{code}\n{nombre[:15]}", fontsize=6,
                             ha="center", va="bottom", color="black", zorder=4)

        self.canvas.draw()

    def verificar_conexidad(self):
        es_conexo, comps = self.grafo.es_conexo()
        print("\n--- CONEXIDAD ---")
        print(f"¿Es conexo? {'Sí' if es_conexo else 'No'}")
        for i, c in enumerate(comps, 1):
            print(f"  Componente {i}: {len(c)} aeropuertos")
        self.mostrar_grafo()

    def mst(self):
        _, comps = self.grafo.es_conexo()
        print("\n--- ÁRBOL DE EXPANSIÓN MÍNIMA ---")
        for i, comp in enumerate(comps, 1):
            peso, aristas = self.grafo.prim_mst(comp)
            print(f"Componente {i} - Peso total: {peso:.2f} km")
        if comps:
            peso, aristas = self.grafo.prim_mst(comps[0])
            sub = {}
            for u, v, w in aristas:
                sub.setdefault(u, {})[v] = w
                sub.setdefault(v, {})[u] = w
            self.mostrar_grafo(sub, color_aristas="#50C878", color_nodos="#E87461")

    def mas_lejanos(self):
        code = self.entry_codigo.get().strip().upper()
        if not code:
            messagebox.showwarning("Atención", "Ingrese código de aeropuerto.")
            return
        print(f"\n--- 10 MÁS LEJANOS DESDE {code} ---")
        self.grafo.aeropuertos_mas_lejanos(code)

    def camino_minimo(self):
        origen = self.entry_origen.get().strip().upper()
        destino = self.entry_destino.get().strip().upper()
        if not origen or not destino:
            messagebox.showwarning("Atención", "Ingrese ambos aeropuertos.")
            return
        dist, pred = self.grafo.dijkstra(origen)
        if dist.get(destino, float("inf")) == float("inf"):
            messagebox.showerror("Sin conexión", "No hay camino.")
            return

        camino = []
        cur = destino
        while cur:
            camino.append(cur)
            cur = pred[cur]
        camino.reverse()

        print(f"\n--- CAMINO MÍNIMO {origen} → {destino} ---")
        for i, code in enumerate(camino, 1):
            info = self.grafo.aeropuertos.get(code, {})
            print(f"{i}. {code} — {info.get('nombre', '')}")
        print(f"Distancia total: {dist[destino]:.2f} km\n")

        sub = {}
        for i in range(len(camino) - 1):
            u, v = camino[i], camino[i + 1]
            w = self.grafo.grafo[u][v]
            sub.setdefault(u, {})[v] = w
            sub.setdefault(v, {})[u] = w
        self.mostrar_grafo(sub, color_aristas="#E74C3C", color_nodos="#F4D03F")

    # ===== MOVIMIENTO Y ZOOM =====
    def _zoom_key(self, zoom_in):
        self.zoom_scale *= self.zoom_step if zoom_in else 1 / self.zoom_step
        self.zoom_scale = max(0.5, min(self.zoom_scale, 5.0))
        self.mostrar_grafo(self._subgrafo_actual, self._color_aristas, self._color_nodos)

    def _move_view(self, dx, dy):
        factor = 5 / self.zoom_scale
        self.pan_x += dx * factor
        self.pan_y += dy * factor
        self.mostrar_grafo(self._subgrafo_actual, self._color_aristas, self._color_nodos)


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazGrafo(root)
    root.mainloop()
