from grafo_aereopuertos import GrafoAeropuertos
import os

def main():
    print("=== SISTEMA DE AEROPUERTOS - GABO Y VALEN ===")
    
    grafo = GrafoAeropuertos()
    
    # gabriel mk hazme el 2 ahí de verificar cual de estas rutas es la correcta, malparido csv
    posibles_rutas = [
        'flights_final.csv',                                      # Misma carpeta
        '../flights_final.csv',                                   # Carpeta padre
        'data/flights_final.csv',                                 # Subcarpeta data
        '../data/flights_final.csv',                              # Padre/data
        'Lab2-Airport-main/flights_final.csv',                    # Subcarpeta Lab2-Airport-main
        'Lab2-Airport-main/data/flights_final.csv',               # Subcarpeta/data
    ]
    
    archivo_csv = None
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            archivo_csv = ruta
            print(f"CSV encontrado en: {ruta}")
            break
    
    if not archivo_csv:
        print("No se pudo encontrar el archivo flights_final.csv")
        print("Buscando archivos CSV en el directorio actual...")
        
        # Buscar recursivamente
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.csv'):
                    ruta_completa = os.path.join(root, file)
                    print(f"CSV encontrado: {ruta_completa}")
                    # Preguntar si usar este archivo
                    usar = input(f"¿Usar este archivo? (s/n): ").strip().lower()
                    if usar == 's':
                        archivo_csv = ruta_completa
                        break
            if archivo_csv:
                break
        
        if not archivo_csv:
            print("❌ No se encontró ningún archivo CSV")
            return
    
    # Cargar datos
    if not grafo.cargar_datos(archivo_csv):
        return
    
    # Resto de tu menú...
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
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida")

if __name__ == "__main__":
    main()
