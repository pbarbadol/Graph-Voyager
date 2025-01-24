import networkx as nx
import random

class GraphAnalyzer:
    def __init__(self, graph):
        """
        Inicializa la clase con un objeto grafo.
        :param graph: Objeto grafo de NetworkX.
        """
        self.graph = graph
        # Determina si el grafo es ponderado
        self.weighted = any('weight' in data for _, _, data in graph.edges(data=True))
        # Determina si el grafo es dirigido
        self.directed = graph.is_directed()

    def betweenness_centrality(self, mode="nodes"):
        """
        Calcula la centralidad de intermediación.
        :param mode: 'nodes' o 'edges' para calcular centralidad en nodos o aristas.
        :return: Diccionario con las centralidades.
        """
        if mode == "nodes":
            if self.weighted:
                return nx.betweenness_centrality(self.graph, weight='weight')
            else:
                return nx.betweenness_centrality(self.graph)
        elif mode == "edges":
            if self.weighted:
                return nx.edge_betweenness_centrality(self.graph, weight='weight')
            else:
                return nx.edge_betweenness_centrality(self.graph)
        else:
            raise ValueError("El modo debe ser 'nodes' o 'edges'.")

    def closeness_centrality(self):
        """
        Calcula la centralidad de cercanía.
        :return: Diccionario con las centralidades.
        """
        if self.weighted:
            return nx.closeness_centrality(self.graph, distance='weight')
        else:
            return nx.closeness_centrality(self.graph)

    def eigenvector_centrality(self, max_iter=100, tol=1e-6):
        """
        Calcula la centralidad de autovalor.
        :param max_iter: Máximo número de iteraciones permitidas.
        :param tol: Tolerancia para la convergencia.
        :return: Diccionario con las centralidades o mensaje de error.
        """
        try:
            if self.weighted:
                return nx.eigenvector_centrality(self.graph, max_iter=max_iter, tol=tol, weight='weight')
            else:
                return nx.eigenvector_centrality(self.graph, max_iter=max_iter, tol=tol)
        except nx.PowerIterationFailedConvergence as e:
            return {"error": f"No se pudo calcular la centralidad de autovalor: {str(e)}"}

    def degree_distribution(self):
        """
        Calcula el grado y la distribución de grados.
        :return: Diccionario con grados y distribución.
        """
        degrees = [d for _, d in self.graph.degree()]
        distribution = {deg: degrees.count(deg) for deg in set(degrees)}
        return {"degrees": degrees, "distribution": distribution}

    def clustering_coefficient(self, sampled=False, sample_size=100):
        """
        Calcula el coeficiente de agrupación.
        :param sampled: Si True, usa una muestra de nodos para el cálculo.
        :param sample_size: Tamaño de la muestra si se usa el muestreo.
        :return: Promedio de clustering y coeficientes individuales.
        """
        if sampled:
            nodes = random.sample(self.graph.nodes(), min(sample_size, len(self.graph.nodes())))
            avg_clustering = nx.average_clustering(self.graph, nodes=nodes, weight='weight' if self.weighted else None)
        else:
            avg_clustering = nx.average_clustering(self.graph, weight='weight' if self.weighted else None)
        node_clustering = nx.clustering(self.graph, weight='weight' if self.weighted else None)
        return {"average": avg_clustering, "individual": node_clustering}

    def connectivity(self, samples=10):
        """
        Calcula la conectividad mediante caminos aleatorios y distancias.
        :param samples: Número de pares de nodos para calcular distancias aleatorias.
        :return: Promedio de distancia entre nodos muestreados.
        """
        nodes = list(self.graph.nodes())
        if len(nodes) < 2:
            raise ValueError("El grafo debe tener al menos dos nodos.")
        
        # Filtrar componentes conectadas
        if not self.directed:
            components = list(nx.connected_components(self.graph))
        else:
            components = list(nx.strongly_connected_components(self.graph))

        if len(components) > 1:
            # Elegir una componente conectada aleatoriamente para evitar nodos sin camino
            nodes = list(random.choice(components))
        
        distances = []
        for _ in range(samples):
            u, v = random.sample(nodes, 2)
            try:
                dist = nx.shortest_path_length(self.graph, source=u, target=v, weight='weight' if self.weighted else None)
                distances.append(dist)
            except nx.NetworkXNoPath:
                distances.append(float('inf'))
        avg_distance = sum(distances) / len(distances)
        return {"average_distance": avg_distance, "distances": distances}
