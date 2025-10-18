import pandas as pd
import heapq
import math
from collections import deque

class GrafoAeropuertos:
    def __init__(self):
        self.aeropuertos = {}  # {codigo: {nombre, ciudad, pais, latitud, longitud}}
        self.grafo = {}        # {codigo: {codigo_vecino: distancia}}
    
    def calcular_distancia(self, lat1, lon1, lat2, lon2):
        """Calcula distancia en km entre dos coordenadas usando fórmula haversine"""
        R = 6371.0  # Radio de la Tierra en km
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distancia = R * c
        return round(distancia, 2)
    
    def cargar_datos(self, ruta_csv):
        """Construye el grafo no dirigido y ponderado"""
        try:
            df = pd.read_csv(ruta_csv)
            print(f"CSV cargado: {len(df)} registros")
            
            # Inicializar estructura del grafo
            for _, fila in df.iterrows():
                origen = fila['Source Airport Code']
                destino = fila['Destination Airport Code']
                
                # Agregar aeropuertos al diccionario
                if origen not in self.aeropuertos:
                    self.aeropuertos[origen] = {
                        'nombre': fila['Source Airport Name'],
                        'ciudad': fila['Source Airport City'],
                        'pais': fila['Source Airport Country'],
                        'latitud': fila['Source Airport Latitude'],
                        'longitud': fila['Source Airport Longitude']
                    }
                    self.grafo[origen] = {}
                
                if destino not in self.aeropuertos:
                    self.aeropuertos[destino] = {
                        'nombre': fila['Destination Airport Name'],
                        'ciudad': fila['Destination Airport City'],
                        'pais': fila['Destination Airport Country'],
                        'latitud': fila['Destination Airport Latitude'],
                        'longitud': fila['Destination Airport Longitude']
                    }
                    self.grafo[destino] = {}
                
                # Calcular distancia y agregar arista no dirigida
                lat1 = fila['Source Airport Latitude']
                lon1 = fila['Source Airport Longitude']
                lat2 = fila['Destination Airport Latitude']
                lon2 = fila['Destination Airport Longitude']
                
                distancia = self.calcular_distancia(lat1, lon1, lat2, lon2)
                
                # Grafo no dirigido - conexión bidireccional
                self.grafo[origen][destino] = distancia
                self.grafo[destino][origen] = distancia
            
            print(f"Grafo construido: {len(self.aeropuertos)} vértices, {sum(len(vecinos) for vecinos in self.grafo.values())//2} aristas")
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def es_conexo(self):
        """Determina si el grafo es conexo y encuentra componentes conexas"""
        visitados = set()
        componentes = []
        
        for aeropuerto in self.grafo:
            if aeropuerto not in visitados:
                # BFS para encontrar componente conexa
                componente = []
                cola = deque([aeropuerto])
                visitados.add(aeropuerto)
                
                while cola:
                    actual = cola.popleft()
                    componente.append(actual)
                    
                    for vecino in self.grafo[actual]:
                        if vecino not in visitados:
                            visitados.add(vecino)
                            cola.append(vecino)
                
                componentes.append(componente)
        
        es_conexo = len(componentes) == 1
        
        print(f"\n--- CONEXIDAD DEL GRAFO ---")
        print(f"¿Es conexo? {'SÍ' if es_conexo else 'NO'}")
        print(f"Número de componentes conexas: {len(componentes)}")
        
        for i, comp in enumerate(componentes, 1):
            print(f"Componente {i}: {len(comp)} aeropuertos")
            if len(comp) <= 10:  # Mostrar solo si son pocos
                print(f"  Aeropuertos: {comp}")
        
        return es_conexo, componentes
    
    def prim_mst(self, componente=None):
        """Algoritmo de Prim para encontrar el árbol de expansión mínima""" #uso prim pq la vd me da ql pava entender los otros y yo me parcho
        if componente is None:
            componente = list(self.grafo.keys())
        
        if not componente:
            return 0, []
        
        visitados = set()
        heap = []
        peso_total = 0
        aristas_mst = []
        
        # Comenzar con el primer aeropuerto de la componente
        inicio = componente[0]
        visitados.add(inicio)
        
        # Agregar todas las aristas desde el inicio
        for vecino, peso in self.grafo[inicio].items():
            if vecino in componente:
                heapq.heappush(heap, (peso, inicio, vecino))
        
        while heap and len(visitados) < len(componente):
            peso, u, v = heapq.heappop(heap)
            
            if v not in visitados:
                visitados.add(v)
                peso_total += peso
                aristas_mst.append((u, v, peso))
                
                # Agregar aristas del nuevo vértice
                for vecino, peso_vecino in self.grafo[v].items():
                    if vecino in componente and vecino not in visitados:
                        heapq.heappush(heap, (peso_vecino, v, vecino))
        
        return peso_total, aristas_mst
    
    def peso_arbol_expansion_minima(self):
        """Calcula el peso del árbol de expansión mínima para cada componente"""
        _, componentes = self.es_conexo()
        
        print(f"\n--- ÁRBOL DE EXPANSIÓN MÍNIMA ---")
        
        for i, comp in enumerate(componentes, 1):
            peso, aristas = self.prim_mst(comp)
            print(f"Componente {i} ({len(comp)} aeropuertos):")
            print(f"  Peso total del MST: {peso:.2f} km")
            print(f"  Número de aristas en MST: {len(aristas)}")
        
        return peso
    
    def dijkstra(self, origen):
        """Algoritmo de Dijkstra para todos los caminos mínimos desde un vértice"""
        distancias = {a: float('inf') for a in self.grafo}
        predecesores = {a: None for a in self.grafo}
        distancias[origen] = 0
        
        heap = [(0, origen)]
        
        while heap:
            dist_actual, actual = heapq.heappop(heap)
            
            if dist_actual > distancias[actual]:
                continue
            
            for vecino, peso in self.grafo[actual].items():
                nueva_dist = dist_actual + peso
                if nueva_dist < distancias[vecino]:
                    distancias[vecino] = nueva_dist
                    predecesores[vecino] = actual
                    heapq.heappush(heap, (nueva_dist, vecino))
        
        return distancias, predecesores
    
    def aeropuertos_mas_lejanos(self, codigo):
        """Encuentra los 10 aeropuertos con caminos mínimos más largos"""
        if codigo not in self.aeropuertos:
            print(f" Aeropuerto {codigo} no encontrado")
            return
        
        distancias, _ = self.dijkstra(codigo)
        
        # Filtrar aeropuertos alcanzables y ordenar por distancia
        alcanzables = [(aero, dist) for aero, dist in distancias.items() 
                      if dist != float('inf') and aero != codigo]
        alcanzables.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n--- 10 AEROPUERTOS MÁS LEJANOS DESDE {codigo} ---")
        print(f"Información de {codigo}:")
        info = self.aeropuertos[codigo]
        print(f"  Nombre: {info['nombre']}")
        print(f"  Ciudad: {info['ciudad']}")
        print(f"  País: {info['pais']}")
        print(f"  Coordenadas: ({info['latitud']}, {info['longitud']})")
        
        print(f"\nAeropuertos más lejanos:")
        for i, (aero, dist) in enumerate(alcanzables[:10], 1):
            info_aero = self.aeropuertos[aero]
            print(f"{i}. {aero} - {info_aero['nombre']}")
            print(f"   Ciudad: {info_aero['ciudad']}, País: {info_aero['pais']}")
            print(f"   Coordenadas: ({info_aero['latitud']}, {info_aero['longitud']})")
            print(f"   Distancia: {dist:.2f} km")
            print()
    
    def camino_minimo(self, origen, destino):
        """Encuentra el camino mínimo entre dos aeropuertos"""
        if origen not in self.aeropuertos:
            print(f"Aeropuerto {origen} no encontrado")
            return
        if destino not in self.aeropuertos:
            print(f"Aeropuerto {destino} no encontrado")
            return
        
        distancias, predecesores = self.dijkstra(origen)
        
        if distancias[destino] == float('inf'):
            print(f"No hay camino entre {origen} y {destino}")
            return
        
        # Reconstruir camino
        camino = []
        actual = destino
        while actual is not None:
            camino.append(actual)
            actual = predecesores[actual]
        camino.reverse()
        
        print(f"\n--- CAMINO MÍNIMO: {origen} → {destino} ---")
        print(f"Distancia total: {distancias[destino]:.2f} km")
        print(f"Ruta: {' → '.join(camino)}")
        
        print(f"\nDetalles del camino:")
        for i, aeropuerto in enumerate(camino):
            info = self.aeropuertos[aeropuerto]
            print(f"{i+1}. {aeropuerto} - {info['nombre']}")
            print(f"   Ciudad: {info['ciudad']}, País: {info['pais']}")
            print(f"   Coordenadas: ({info['latitud']}, {info['longitud']})")
            
            if i < len(camino) - 1:
                siguiente = camino[i+1]
                distancia_etapa = self.grafo[aeropuerto][siguiente]
                print(f"   → Siguiente: {siguiente} ({distancia_etapa} km)")
            print()
    