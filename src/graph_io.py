import networkx as nx
import pandas as pd

class GraphIO:
    def __init__(self, graph=None):
        """
        Inicializa la clase para importar y exportar grafos.
        :param graph: Objeto grafo de NetworkX (opcional).
        """
        self.graph = graph if graph else nx.Graph()

    def import_graph(self, file_format, file_paths):
        """
        Importa un grafo desde uno o varios archivos.
        :param file_format: Formato del archivo ('csv', 'gml', 'graphml', 'edgelist').
        :param file_paths: Ruta(s) de archivo. Puede ser un string (1 archivo) o una lista (2 archivos: [edges, target]).
        """
        try:
            if file_format == "csv":
                if isinstance(file_paths, list) and len(file_paths) == 2:
                    # Caso: dos archivos CSV (edges y target)
                    self._load_graph_from_csv(edges_file=file_paths[0], nodes_file=file_paths[1])
                elif isinstance(file_paths, str):
                    # Caso: un solo archivo CSV
                    self._load_graph_from_csv(edges_file=file_paths)
                else:
                    raise ValueError("Para CSV, file_paths debe ser un string (1 archivo) o una lista de 2 archivos.")
            else:
                # Cargar otros formatos de archivo
                self._load_graph_from_file(file_paths, file_format)
            print(f"Grafo importado con éxito desde {file_paths}.")
        except Exception as e:
            print(f"Error al importar el grafo: {e}")

    def export_graph(self, file_path, file_format):
        """
        Exporta el grafo actual al formato especificado.
        :param file_path: Ruta del archivo de salida.
        :param file_format: Formato de salida ('csv', 'gml', 'graphml', 'edgelist').
        """
        try:
            # Convertir nodos a cadenas si el formato lo requiere
            if file_format in ["gml", "graphml"]:
                self.graph = nx.relabel_nodes(self.graph, lambda x: str(x))

            if file_format == "csv":
                edges = nx.to_pandas_edgelist(self.graph)
                edges.to_csv(file_path, index=False)
            elif file_format == "gml":
                nx.write_gml(self.graph, file_path)
            elif file_format == "graphml":
                nx.write_graphml(self.graph, file_path)
            elif file_format == "edgelist":
                nx.write_edgelist(self.graph, file_path)
            else:
                raise ValueError("Formato de archivo no soportado.")
            print(f"Grafo exportado con éxito a {file_path}.")
        except Exception as e:
            print(f"Error al exportar el grafo: {e}")


    def _load_graph_from_csv(self, edges_file, nodes_file=None):
        """
        Carga un grafo desde archivos CSV de nodos y aristas.
        :param edges_file: Ruta al archivo CSV que contiene las aristas.
        :param nodes_file: Ruta al archivo CSV que contiene los nodos (opcional).
        """
        try:
            edges_df = pd.read_csv(edges_file)
            if "id_1" in edges_df.columns and "id_2" in edges_df.columns:
                self.graph.add_edges_from(edges_df[["id_1", "id_2"]].values)
            else:
                raise ValueError("El archivo de aristas debe contener columnas 'id_1' y 'id_2'.")
            print("Aristas cargadas con éxito.")

            if nodes_file:
                nodes_df = pd.read_csv(nodes_file)
                if "id" not in nodes_df.columns:
                    raise ValueError("El archivo de nodos debe contener la columna 'id'.")
                for _, row in nodes_df.iterrows():
                    node_id = row["id"]
                    attributes = row.to_dict()
                    del attributes["id"]
                    self.graph.add_node(node_id, **attributes)
                print("Nodos cargados con éxito.")
        except Exception as e:
            print(f"Error al cargar el grafo desde CSV: {e}")

    def _load_graph_from_file(self, file_path, file_format):
        """
        Carga un grafo desde un archivo en formatos comunes.
        :param file_path: Ruta al archivo.
        :param file_format: Formato del archivo ('gml', 'graphml', 'edgelist').
        """
        try:
            if file_format == "gml":
                self.graph = nx.read_gml(file_path)
            elif file_format == "graphml":
                self.graph = nx.read_graphml(file_path)
            elif file_format == "edgelist":
                self.graph = nx.read_edgelist(file_path)
            else:
                raise ValueError("Formato de archivo no soportado.")
            print(f"Grafo cargado con éxito desde archivo {file_path}.")
        except Exception as e:
            print(f"Error al cargar el grafo desde archivo: {e}")

    def get_graph(self):
        """
        Devuelve el grafo cargado o modificado.
        :return: Objeto grafo de NetworkX.
        """
        return self.graph
