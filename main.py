from grafo_aereopuertos import GrafoAeropuertos
import os

def main():
    print("=== SISTEMA DE AEROPUERTOS - VALEN Y GABO ===")
    
    grafo = GrafoAeropuertos()

    # Verificación simple del archivo CSV, no es necesario agregar otras rutas
    # , pues el archivo csv está en la misma carpeta
    nombre_csv = "flights_final.csv"
    archivo_csv = None

    if os.path.exists(nombre_csv):
        archivo_csv = nombre_csv
        # en caso de que encontremos el csv, se muestra TOODA la ruta
        print(f"CSV encontrado en: {os.path.abspath(nombre_csv)}")
    else:
        print("No se encontró el archivo flights_final.csv en el directorio main, paila")
        print("Buscando archivos CSV en subcarpetas...")

        for root, _, files in os.walk('.'):
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

    # === Cargamos los datos del grafo ===
    if not grafo.cargar_datos(archivo_csv):
        return
    
    # === Mostramos el menú principal ===
    menu_principal(grafo)

def menu_principal(grafo):
    while True:
        print("\n" + "="*60)
        print("                  MENÚ PRINCIPAL")
        print("="*60)
        print("1. Verificar conexidad del grafo")
        print("2. Calcular árbol de expansión mínima")
        print("3. Información de aeropuerto + 10 más lejanos")
        print("4. Encontrar camino mínimo entre dos aeropuertos")
        print("5. Salir")
        print("-"*60)
        
        opcion = input("Selecciona una opción (1-5): ").strip()
        
        if opcion == '1':
            grafo.es_conexo()
        elif opcion == '2':
            grafo.peso_arbol_expansion_minima()
        elif opcion == '3':
            codigo = input("Código del aeropuerto (ej: ATL, JFK, LAX): ").strip().upper()
            grafo.aeropuertos_mas_lejanos(codigo)
        elif opcion == '4':
            origen = input("Código del aeropuerto origen: ").strip().upper()
            destino = input("Código del aeropuerto destino: ").strip().upper()
            grafo.camino_minimo(origen, destino)
        elif opcion == '5':
            print("Hasta luego cachón!")
            break
        else:
            print("Opción inválida 😂😂😂, intente nuevamente.")

if __name__ == "__main__":
    main()
