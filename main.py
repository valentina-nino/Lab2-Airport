from grafo_aereopuertos import GrafoAeropuertos
import os

def main():
    print("=== SISTEMA DE AEROPUERTOS - GABO Y VALEN ===")
    
    #luis camilo le rompe el anillo a chiqui
    grafo = GrafoAeropuertos()
    
    # Cargar datos
    if not grafo.cargar_datos('flights_final.csv'):
        return
    
    # Menú principal
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
            codigo = input("Código del aeropuerto (ej: CDG, JFK, LAX): ").strip().upper()
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
