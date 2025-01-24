from neo4j import GraphDatabase
import networkx as nx

class Neo4jManager:
    def __init__(self, uri, user, password):
        """
        Inicializa la conexión con Neo4j.
        :param uri: URI de la base de datos (e.g., bolt://localhost:7687)
        :param user: Usuario de Neo4j.
        :param password: Contraseña de Neo4j.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
        Cierra la conexión con Neo4j.
        """
        self.driver.close()

    def clear_database(self):
        """
        Limpia toda la base de datos (elimina todos los nodos y relaciones).
        """
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def upload_graph(self, graph):
        """
        Sube un grafo de NetworkX a Neo4j.
        :param graph: Objeto grafo de NetworkX.
        """
        with self.driver.session() as session:
            # Subir nodos
            for node, attributes in graph.nodes(data=True):
                normalized_attributes = self._normalize_properties(attributes)
                print(f"[DEBUG] Nodo: {node}, Atributos originales: {attributes}, Normalizados: {normalized_attributes}")
                
                # Construir la consulta con propiedades dinámicas
                properties = ", ".join([f"{key}: ${key}" for key in normalized_attributes.keys()])
                query = f"CREATE (n:Node {{id: $id, {properties}}})"
                
                # Ejecutar la consulta con los parámetros normalizados
                session.run(query, id=node, **normalized_attributes)

            # Subir relaciones
            for start, end, attributes in graph.edges(data=True):
                normalized_attributes = self._normalize_properties(attributes)
                print(f"[DEBUG] Relación: {start} -> {end}, Atributos originales: {attributes}, Normalizados: {normalized_attributes}")
                
                # Construir la consulta con propiedades dinámicas
                properties = ", ".join([f"{key}: ${key}" for key in normalized_attributes.keys()])
                query = f"""
                    MATCH (a:Node {{id: $start_id}}), (b:Node {{id: $end_id}})
                    CREATE (a)-[r:RELATIONSHIP {{{properties}}}]->(b)
                """
                
                # Ejecutar la consulta con los parámetros normalizados
                session.run(query, start_id=start, end_id=end, **normalized_attributes)







    def _normalize_properties(self, properties):
        """
        Normaliza las propiedades de nodos y relaciones para que sean compatibles con Neo4j.
        :param properties: Diccionario de propiedades.
        :return: Diccionario normalizado.
        """
        normalized = {}
        for key, value in properties.items():
            try:
                # Si el valor es un diccionario o lista, serializar a JSON
                if isinstance(value, (dict, list)):
                    normalized[key] = json.dumps(value)
                # Si es un tipo primitivo compatible, dejarlo tal cual
                elif isinstance(value, (int, float, str, bool)) or value is None:
                    normalized[key] = value
                # Si detectamos un objeto numérico tipo Long
                elif isinstance(value, int) or "Long" in str(type(value)):
                    normalized[key] = int(value)
                # Si el valor no es compatible, convertirlo a cadena como último recurso
                else:
                    normalized[key] = str(value)
            except Exception as e:
                print(f"Error al normalizar la propiedad {key}: {value}. {e}")
                normalized[key] = str(value)  # Convertir a cadena en caso de error
        return normalized




    def download_graph(self):
        """
        Descarga los nodos y relaciones desde Neo4j y los convierte en un grafo de NetworkX.
        :return: Objeto grafo de NetworkX.
        """
        graph = nx.DiGraph()  # Grafo dirigido
        with self.driver.session() as session:
            # Descargar nodos
            nodes = session.run("MATCH (n) RETURN n")
            for record in nodes:
                node = record["n"]
                graph.add_node(node.id, **node._properties)

            # Descargar relaciones
            edges = session.run("MATCH (n)-[r]->(m) RETURN n, r, m")
            for record in edges:
                start_node = record["n"]
                end_node = record["m"]
                relationship = record["r"]
                graph.add_edge(
                    start_node.id,
                    end_node.id,
                    **relationship._properties
                )
        return graph

    def execute_query(self, query):
        """
        Ejecuta una consulta Cypher en Neo4j.
        :param query: Cadena de texto con la consulta Cypher.
        :return: Lista de resultados como diccionarios.
        """
        with self.driver.session() as session:
            results = session.run(query)
            # Convertir resultados en una lista de diccionarios
            return [dict(record) for record in results]
