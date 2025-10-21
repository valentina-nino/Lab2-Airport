from grafo_aereopuertos import GrafoAeropuertos
from interfaz_grafo import InterfazGrafo
import os
import tkinter as tk

def main():
    print("=== SISTEMA DE AEROPUERTOS - VALEN Y GABO ===")

    grafo = GrafoAeropuertos()

    # Ruta absoluta del CSV en la misma carpeta del script
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    nombre_csv = os.path.join(ruta_base, "flights_final.csv")

    if os.path.exists(nombre_csv):
        print(f"CSV encontrado en: {nombre_csv}")
        archivo_csv = nombre_csv
    else:
        print("No se encontró 'flights_final.csv' en la carpeta del proyecto.")
        print("Buscando archivos CSV en subcarpetas...")

        archivo_csv = None
        for root, _, files in os.walk(ruta_base):
            for file in files:
                if file.endswith('.csv'):
                    ruta_completa = os.path.join(root, file)
                    print(f"Encontrado: {ruta_completa}")
                    usar = input("¿Usar este archivo? (s/n): ").strip().lower()
                    if usar == 's':
                        archivo_csv = ruta_completa
                        break
            if archivo_csv:
                break

        if not archivo_csv:
            print("No se encontró ningún archivo CSV válido.")
            return

    # === Cargar datos ===
    if not grafo.cargar_datos(archivo_csv):
        print("Error al cargar los datos.")
        return

    # === Lanzar interfaz gráfica ===
    root = tk.Tk()
    app = InterfazGrafo(root, grafo)
    root.mainloop()

if __name__ == "__main__":
    main()
