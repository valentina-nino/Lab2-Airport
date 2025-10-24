import tkinter as tk
from tkinter import messagebox
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
        self._subgrafo_actual = None
        self._color_aristas = "#444"
        self._color_nodos = "#007ACC"
        self._pos_cache = None

        sys.stdout = self  # Redirigir print al cuadro de texto

        # ====== FRAME SUPERIOR ======
        frame_botones = tk.Frame(self.root, bg="#e0e6eb", pady=8)
        frame_botones.pack(fill=tk.X)

        tk.Button(frame_botones, text="Refrescar grafo",
                  command=self.mostrar_grafo_completo, width=14,
                  bg="#4A90E2", fg="white").pack(side=tk.LEFT, padx=6)
        tk.Button(frame_botones, text="Verificar Conexidad",
                  command=self.verificar_conexidad, width=18,
                  bg="#4A90E2", fg="white").pack(side=tk.LEFT, padx=6)
        tk.Button(frame_botones, text="Árbol Exp. Mínima",
                  command=self.mst, width=16, bg="#4A90E2",
                  fg="white").pack(side=tk.LEFT, padx=6)

        tk.Label(frame_botones, text="Origen:", bg="#e0e6eb").pack(side=tk.LEFT, padx=(12, 2))
        self.entry_origen = tk.Entry(frame_botones, width=8)
        self.entry_origen.pack(side=tk.LEFT, padx=4)
        tk.Label(frame_botones, text="Destino:", bg="#e0e6eb").pack(side=tk.LEFT, padx=(8, 2))
        self.entry_destino = tk.Entry(frame_botones, width=8)
        self.entry_destino.pack(side=tk.LEFT, padx=4)
        tk.Button(frame_botones, text="Camino mínimo",
                  command=self.camino_minimo, width=14,
                  bg="#50C878", fg="white").pack(side=tk.LEFT, padx=6)

        tk.Label(frame_botones, text="Código:", bg="#e0e6eb").pack(side=tk.LEFT, padx=(12, 2))
        self.entry_codigo = tk.Entry(frame_botones, width=8)
        self.entry_codigo.pack(side=tk.LEFT, padx=4)
        tk.Button(frame_botones, text="Top 10 más lejanos",
                  command=self.mas_lejanos, width=16,
                  bg="#50C878", fg="white").pack(side=tk.LEFT, padx=6)

        instr = "Zoom: W/S | Mover: ← ↑ ↓ → | Esc: salir fullscreen"
        tk.Label(frame_botones, text=instr, bg="#e0e6eb", fg="#333").pack(side=tk.RIGHT, padx=10)

        # Eventos de teclado
        self.root.bind("w", lambda e: self._zoom_key(True))
        self.root.bind("s", lambda e: self._zoom_key(False))
        self.root.bind("<Up>", lambda e: self._move_view(0, 10))
        self.root.bind("<Down>", lambda e: self._move_view(0, -10))
        self.root.bind("<Left>", lambda e: self._move_view(-10, 0))
        self.root.bind("<Right>", lambda e: self._move_view(10, 0))

        # ====== FRAME CENTRAL ======
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

        # ====== FRAME INFERIOR ======
        frame_salida = tk.Frame(self.root)
        frame_salida.pack(fill=tk.BOTH, padx=10, pady=8)
        tk.Label(frame_salida, text="Salida de información:", bg="#f0f4f7").pack(anchor="w")
        self.text_salida = tk.Text(frame_salida, height=9, wrap=tk.WORD, bg="#f7f9fa")
        self.text_salida.pack(fill=tk.BOTH, expand=True)
        self.text_salida.insert(tk.END, "Bienvenido al sistema de aeropuertos.\n")

        # Mostrar grafo completo al inicio
        if self.grafo.grafo:
            self.root.after(300, self.mostrar_grafo_completo)

    # ====== AUXILIARES ======
    def _cargar_mapa_fondo(self):
        """
        Carga el archivo local 'mapamundi_fondo.png' y lo prepara como fondo del grafo.
        - Admite JPG o PNG.
        - Si el PNG tiene transparencia, la elimina para que se vea bien detrás.
        - Redimensiona la imagen para ajustarse a los límites geográficos del mapa.
        """
        archivo = "mapamundi_fondo.png"  # Asegúrate de que esté en la misma carpeta que este .py

        if not os.path.exists(archivo):
            print("⚠️ No se encontró el archivo 'mapamundi_fondo.png' en la carpeta del proyecto.")
            print("Por favor, colócalo junto a 'interfaz_grafo.py'.")
            return None

        try:
            from PIL import Image
            import matplotlib.image as mpimg

            # Abrir y convertir la imagen
            img = Image.open(archivo).convert("RGBA")

            # Si tiene transparencia (canal alfa), eliminarla
            if img.mode == "RGBA":
                fondo = Image.new("RGB", img.size, (255, 255, 255))
                fondo.paste(img, mask=img.split()[3])  # elimina la transparencia
                img = fondo

            # Redimensionar para un ancho estándar de mapa
            img = img.resize((2048, 1024))  # se adapta bien a las coordenadas [-180,180]x[-90,90]

            # Guardar temporalmente en formato JPG para cargarlo con matplotlib
            temp_path = "mapamundi_temp.jpg"
            img.save(temp_path, "JPEG", quality=90)

            # Cargar con matplotlib (sin canal alfa, para evitar superposición)
            mapa = mpimg.imread(temp_path)
            print("🗺️ Mapa de fondo cargado exitosamente.")
            return mapa

        except Exception as e:
            print("❌ Error cargando el mapa de fondo:", e)
            return None


    def write(self, texto):
        try:
            self.text_salida.insert(tk.END, texto)
            self.text_salida.see(tk.END)
            sys.__stdout__.write(texto)
        except Exception:
            pass

    def flush(self): pass

    # ====== GRAFO ======
    def _get_positions(self, subgrafo=None):
        if self._pos_cache and not subgrafo:
            return self._pos_cache

        datos = subgrafo if subgrafo else self.grafo.grafo
        pos = {}
        for code, info in self.grafo.aeropuertos.items():
            try:
                pos[code] = (float(info["longitud"]), float(info["latitud"]))
            except:
                continue
        if not subgrafo:
            self._pos_cache = pos
        return pos

    def mostrar_grafo_completo(self):
        self._reset_zoom()
        self._subgrafo_actual = None
        self.mostrar_grafo(self.grafo.grafo)

    def mostrar_grafo(self, subgrafo=None, color_aristas="#444", color_nodos="#007ACC"):
        self._subgrafo_actual = subgrafo
        self._color_aristas = color_aristas
        self._color_nodos = color_nodos

        self.ax.clear()
        if self.mapa is not None:
            self.ax.imshow(self.mapa, extent=[-180, 180, -90, 90], zorder=0)
        else:
            self.ax.set_facecolor("#E0E0E0")

        x_min, x_max = (-180 / self.zoom_scale) + self.pan_x, (180 / self.zoom_scale) + self.pan_x
        y_min, y_max = (-90 / self.zoom_scale) + self.pan_y, (90 / self.zoom_scale) + self.pan_y
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.ax.set_axis_off()

        datos = subgrafo if subgrafo else self.grafo.grafo
        pos = self._get_positions(subgrafo)
        segmentos = [[pos[u], pos[v]] for u in datos for v in datos[u] if u in pos and v in pos]
        if segmentos:
            self.ax.add_collection(LineCollection(segmentos, linewidths=0.4, colors=color_aristas, alpha=0.5, zorder=2))

        xs, ys = zip(*pos.values())
        self.ax.scatter(xs, ys, s=15, c=color_nodos, alpha=0.8, zorder=3)

        if len(pos) < 200 or self.zoom_scale > 1.8:
            for code, (x, y) in pos.items():
                nombre = self.grafo.aeropuertos.get(code, {}).get("nombre", "")
                self.ax.text(x, y, f"{code}\n{nombre[:15]}", fontsize=6,
                             ha="center", va="bottom", color="black", zorder=4)

        self.canvas.draw_idle()

    # ====== FUNCIONALIDAD ======
    def verificar_conexidad(self):
        self._reset_zoom()

        es_conexo, comps = self.grafo.es_conexo()
        print("\n--- CONEXIDAD ---")
        print(f"¿Es conexo? {'Sí' if es_conexo else 'No'}")

        for i, comp in enumerate(comps, 1):
            peso, _ = self.grafo.prim_mst(comp)
            print(f"  Componente {i}: {len(comp)} aeropuertos — Distancia total: {peso:.2f} km")

        self.mostrar_grafo()

    def mst(self):
        self._reset_zoom()
        _, comps = self.grafo.es_conexo()
        print("\n--- ÁRBOL DE EXPANSIÓN MÍNIMA ---")
        for i, comp in enumerate(comps, 1):
            peso, aristas = self.grafo.prim_mst(comp)
            print(f"Componente {i}: {len(comp)} aeropuertos — Peso total: {peso:.2f} km")
        if comps:
            peso, aristas = self.grafo.prim_mst(comps[0])
            sub = {}
            for u, v, w in aristas:
                sub.setdefault(u, {})[v] = w
                sub.setdefault(v, {})[u] = w
            self.mostrar_grafo(sub, color_aristas="#50C878", color_nodos="#E87461")

    def mas_lejanos(self):
        self._reset_zoom()
        code = self.entry_codigo.get().strip().upper()
        if not code:
            messagebox.showwarning("Atención", "Ingrese código de aeropuerto.")
            return
        print(f"\n--- 10 MÁS LEJANOS DESDE {code} ---")
        self.grafo.aeropuertos_mas_lejanos(code)

    def camino_minimo(self):
        self._reset_zoom()

        """
        Dibuja ÚNICAMENTE el camino mínimo entre dos aeropuertos (origen → destino),
        y mantiene el control de zoom/pan sobre ese camino.
        """
        origen = self.entry_origen.get().strip().upper()
        destino = self.entry_destino.get().strip().upper()

        if not origen or not destino:
            messagebox.showwarning("Atención", "Ingrese ambos aeropuertos.")
            return

        dist, pred = self.grafo.dijkstra(origen)
        if dist.get(destino, float("inf")) == float("inf"):
            messagebox.showerror("Sin conexión", "No hay camino disponible.")
            return

        # reconstruir el camino
        camino = []
        cur = destino
        while cur:
            camino.append(cur)
            cur = pred[cur]
        camino.reverse()

        print(f"\n--- CAMINO MÍNIMO {origen} → {destino} ---")
        for i, code in enumerate(camino, 1):
            info = self.grafo.aeropuertos.get(code, {})
            nombre = info.get("nombre", info.get("Source Airport Name", "Desconocido"))
            ciudad = info.get("ciudad", info.get("Source Airport City", "Desconocido"))
            pais = info.get("pais", info.get("Source Airport Country", "Desconocido"))
            lat = info.get("latitud", info.get("Source Airport Latitude", "N/A"))
            lon = info.get("longitud", info.get("Source Airport Longitude", "N/A"))

            print(f"{i}. {code} - {nombre} ({ciudad}, {pais}) [Lat: {lat}, Lon: {lon}]")
        print(f"Distancia total: {dist[destino]:.2f} km\n")

        # construir subgrafo SOLO con las aristas del camino
        sub = {}
        for i in range(len(camino) - 1):
            u, v = camino[i], camino[i + 1]
            w = self.grafo.grafo[u][v]
            sub.setdefault(u, {})[v] = w
            sub.setdefault(v, {})[u] = w

        # Dibujar solo el camino y mantenerlo como subgrafo actual
        self._subgrafo_actual = sub
        self._color_aristas = "#E74C3C"
        self._color_nodos = "#F4D03F"
        self._mostrar_solo_camino(sub, camino)

    def _mostrar_solo_camino(self, subgrafo, nodos_camino):
        """
        Muestra sólo el subgrafo correspondiente al camino mínimo,
        respetando zoom/pan, y permitiendo zoom interactivo.
        """
        self.ax.clear()
        if self.mapa is not None:
            self.ax.imshow(self.mapa, extent=[-180, 180, -90, 90], zorder=0)
        else:
            self.ax.set_facecolor("#E0E0E0")

        # aplicar zoom y desplazamiento actuales
        x_min, x_max = (-180 / self.zoom_scale) + self.pan_x, (180 / self.zoom_scale) + self.pan_x
        y_min, y_max = (-90 / self.zoom_scale) + self.pan_y, (90 / self.zoom_scale) + self.pan_y
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.ax.set_axis_off()

        pos = self._get_positions(subgrafo)

        # dibujar aristas del camino
        segmentos = [[pos[u], pos[v]] for u in subgrafo for v in subgrafo[u] if u in pos and v in pos]
        if segmentos:
            self.ax.add_collection(LineCollection(segmentos, linewidths=1.5, colors="#E74C3C", alpha=0.9, zorder=2))

        # dibujar nodos del camino (resaltados)
        xs = [pos[n][0] for n in nodos_camino if n in pos]
        ys = [pos[n][1] for n in nodos_camino if n in pos]
        self.ax.scatter(xs, ys, s=40, c="#F4D03F", edgecolors="black", linewidths=0.7, zorder=3)

        # etiquetas solo para los nodos del camino
        for code in nodos_camino:
            if code in pos:
                x, y = pos[code]
                nombre = self.grafo.aeropuertos.get(code, {}).get("nombre", "")
                self.ax.text(x, y, f"{code}\n{nombre[:15]}",
                             fontsize=7, ha="center", va="bottom", color="black", zorder=4)

        self.canvas.draw_idle()

    # ====== MOVIMIENTO Y ZOOM ======
    def _zoom_key(self, zoom_in):
        """
        Controla el zoom sobre el subgrafo actual (mantiene vista local).
        """
        self.zoom_scale *= self.zoom_step if zoom_in else 1 / self.zoom_step
        self.zoom_scale = max(0.5, min(self.zoom_scale, 5.0))

        # Redibuja el último subgrafo mostrado (camino, MST, grafo completo)
        if self._subgrafo_actual:
            # Si estamos mostrando un camino mínimo
            if self._color_aristas == "#E74C3C":
                self._mostrar_solo_camino(self._subgrafo_actual, list(self._subgrafo_actual.keys()))
            else:
                self.mostrar_grafo(self._subgrafo_actual, self._color_aristas, self._color_nodos)
        else:
            self.mostrar_grafo(self.grafo.grafo)

    def _reset_zoom(self):
        """
        Restaura el zoom y desplazamiento a los valores por defecto.
        """
        self.zoom_scale = 1.0
        self.pan_x = 0
        self.pan_y = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazGrafo(root)
    root.mainloop()
