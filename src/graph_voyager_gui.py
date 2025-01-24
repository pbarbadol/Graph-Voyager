import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, simpledialog
from PIL import Image, ImageTk
import networkx as nx
import json
import pandas as pd
from graph_io import GraphIO
from graph_analyzer import GraphAnalyzer
from Neo4jManager import Neo4jManager
import matplotlib.pyplot as plt

class GraphVoyagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Voyager")
        self.root.configure(bg="#35313b")  # Color de fondo
        self.graph = None  # Grafo cargado
        self.graph_io = GraphIO()
        self.metrics_results = {}  # Resultados de las métricas

        # Logo
        self.logo_frame = tk.Frame(root, bg="#35313b")
        self.logo_frame.pack(pady=20)
        self.load_logo()

        # Texto de bienvenida
        self.label = tk.Label(root, text="🌌 Bienvenido a Graph Voyager 🌌", font=("Helvetica", 16), bg="#35313b", fg="white")
        self.label.pack(pady=20)

        # Botones
        self.buttons_frame = tk.Frame(root, bg="#35313b")
        self.buttons_frame.pack(pady=20)

        button_style = {"bg": "#5a5566", "fg": "white", "font": ("Helvetica", 12), "width": 20, "height": 2}

        self.load_graph_button = tk.Button(self.buttons_frame, text="Cargar grafo", command=self.load_graph, **button_style)
        self.load_graph_button.grid(row=0, column=0, padx=10, pady=10)

        self.analyze_button = tk.Button(self.buttons_frame, text="Calcular métricas", command=self.analyze_graph, **button_style)
        self.analyze_button.grid(row=0, column=1, padx=10, pady=10)

        self.export_button = tk.Button(self.buttons_frame, text="Exportar métricas", command=self.export_results, **button_style)
        self.export_button.grid(row=0, column=2, padx=10, pady=10)

        self.visualize_button = tk.Button(self.buttons_frame, text="Visualizar grafo", command=self.visualize_graph, **button_style)
        self.visualize_button.grid(row=1, column=0, padx=10, pady=10)

        self.save_as_button = tk.Button(self.buttons_frame, text="Guardar como", command=self.save_as, **button_style)
        self.save_as_button.grid(row=1, column=1, padx=10, pady=10)

        self.neo4j_button = tk.Button(self.buttons_frame, text="Neo4j", command=self.neo4j_integration, **button_style)
        self.neo4j_button.grid(row=1, column=2, padx=10, pady=10)

        # Área de Resultados
        self.results_text = tk.Text(root, height=15, width=80, bg="#2c2a33", fg="white", font=("Consolas", 10))
        self.results_text.pack(pady=20)

        # Firma
        self.signature_label = tk.Label(root, text="Pablo Barbado Lozano - Universidad de Sevilla", font=("Helvetica", 8), bg="#35313b", fg="gray")
        self.signature_label.pack(side=tk.BOTTOM, pady=5)

    def load_logo(self):
        try:
            logo = Image.open("images/logo.png")
            logo = logo.resize((200, 200), Image.Resampling.LANCZOS)
            logo = ImageTk.PhotoImage(logo)
            label = tk.Label(self.logo_frame, image=logo, bg="#35313b")
            label.image = logo  # Mantener referencia
            label.pack()
        except Exception as e:
            print(f"Error al cargar el logo: {e}")

    def load_graph(self):
        file_path = filedialog.askopenfilename(title="Seleccionar Archivo del Grafo")
        if not file_path:
            return

        try:
            file_format = file_path.split('.')[-1]
            self.graph_io.import_graph(file_format, file_path)
            self.graph = self.graph_io.get_graph()

            # Limpiar la terminal
            self.results_text.delete("1.0", tk.END)

            self.results_text.insert(tk.END, f"Grafo cargado desde: {file_path}\n")
            self.results_text.insert(tk.END, f"Número de nodos: {self.graph.number_of_nodes()}\n")
            self.results_text.insert(tk.END, f"Número de aristas: {self.graph.number_of_edges()}\n")
            messagebox.showinfo("Éxito", "Grafo cargado con éxito.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el grafo: {e}")

    def analyze_graph(self):
        if not self.graph:
            messagebox.showwarning("Advertencia", "Cargue un grafo primero.")
            return

        try:
            analyzer = GraphAnalyzer(self.graph)
            # Limpiar resultados previos
            self.results_text.delete("1.0", tk.END)
            self.metrics_results = {
                "Betweenness": analyzer.betweenness_centrality(),
                "Closeness": analyzer.closeness_centrality(),
                "Eigenvector": analyzer.eigenvector_centrality(),
                "Clustering": analyzer.clustering_coefficient()
            }

            # Mostrar métricas globales
            clustering_avg = self.metrics_results["Clustering"]["average"]
            self.results_text.insert(tk.END, "Resultados Globales:\n")
            self.results_text.insert(tk.END, f"- Coeficiente de Clustering Promedio: {clustering_avg:.4f}\n")
            self.results_text.insert(tk.END, "-" * 40 + "\n")

            # Mostrar métricas por nodo en formato tabla
            self.results_text.insert(tk.END, "Métricas por Nodo:\n")
            metrics_by_node = ["Betweenness", "Closeness", "Eigenvector"]
            for metric_name in metrics_by_node:
                self.results_text.insert(tk.END, f"\n{metric_name}:\n")
                for node, value in list(self.metrics_results[metric_name].items())[:10]:  # Mostrar solo los primeros 10
                    self.results_text.insert(tk.END, f"Nodo {node}: {value:.4f}\n")

            messagebox.showinfo("Éxito", "Métricas calculadas con éxito.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron calcular las métricas: {e}")

    def save_as(self):
        if not self.graph:
            messagebox.showwarning("Advertencia", "Cargue un grafo primero.")
            return

        self.show_format_selector("Guardar Grafo", self.save_graph_to_format)

    def save_graph_to_format(self, chosen_format):
        save_path = filedialog.asksaveasfilename(defaultextension=f".{chosen_format.lower()}", title="Guardar Grafo")
        if not save_path:
            return

        try:
            if chosen_format == "GML":
                nx.write_gml(self.graph, save_path)
            elif chosen_format == "GraphML":
                nx.write_graphml(self.graph, save_path)
            elif chosen_format == "Edgelist":
                nx.write_edgelist(self.graph, save_path)
            elif chosen_format == "CSV":
                edges = nx.to_pandas_edgelist(self.graph)
                edges.to_csv(save_path, index=False)
            else:
                raise ValueError("Formato no soportado.")
            messagebox.showinfo("Éxito", f"Grafo guardado como {save_path}.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el grafo: {e}")

    def export_results(self):
        if not self.metrics_results:
            messagebox.showwarning("Advertencia", "Calcule las métricas primero.")
            return

        self.export_metrics_to_format("CSV")

    def export_metrics_to_format(self, chosen_format):
        save_path = filedialog.asksaveasfilename(defaultextension=f".{chosen_format.lower()}", title="Guardar Resultados")
        if not save_path:
            return

        try:
            if chosen_format == "CSV":
                pd.DataFrame.from_dict(self.metrics_results, orient='index').to_csv(save_path)

            else:
                raise ValueError("Formato no soportado.")
            messagebox.showinfo("Éxito", f"Resultados exportados como {save_path}.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron exportar los resultados: {e}")

    def show_format_selector(self, title, callback):
        formats = ["GML", "GraphML", "Edgelist", "CSV"]
        selector_window = Toplevel(self.root)
        selector_window.title(title)
        selector_window.configure(bg="#35313b")
        selector_window.geometry("300x300")
        tk.Label(selector_window, text="Seleccione el formato:", font=("Helvetica", 12), bg="#35313b", fg="white").pack(pady=20)
        for fmt in formats:
            tk.Button(selector_window, text=fmt, command=lambda f=fmt: [callback(f), selector_window.destroy()], width=20, height=2, bg="#5a5566", fg="white").pack(pady=5)

    def visualize_graph(self):
        if not self.graph:
            messagebox.showwarning("Advertencia", "Cargue un grafo primero.")
            return

        # Configuración de la visualización
        try:
            plt.figure(figsize=(8, 8))
            pos = nx.spring_layout(self.graph)  # Layout del grafo
            nx.draw(
                self.graph,
                pos,
                with_labels=True,
                node_color="skyblue",
                node_size=500,
                edge_color="gray",
                font_size=8
            )
            plt.title("Visualización del Grafo")
            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo visualizar el grafo: {e}")

    def neo4j_integration(self):
        """
        Conexión con Neo4j y apertura del menú correspondiente.
        """
        uri = simpledialog.askstring("Neo4j URI", "Introduce el URI de la base de datos (e.g., bolt://localhost:7687):")
        user = simpledialog.askstring("Usuario", "Introduce tu usuario de Neo4j:")
        password = simpledialog.askstring("Contraseña", "Introduce tu contraseña de Neo4j:", show="*")

        try:
            # Crear una instancia de Neo4jManager
            self.neo4j_manager = Neo4jManager(uri, user, password)
            messagebox.showinfo("Éxito", "Conexión con Neo4j exitosa.")
            self.open_neo4j_menu(self.neo4j_manager)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar a Neo4j: {e}")


    def open_neo4j_menu(self, neo4j_manager):
        """
        Abre el menú de Neo4j una vez conectado.
        """
        menu_window = Toplevel(self.root)
        menu_window.title("Menú de Neo4j")
        menu_window.configure(bg="#35313b")
        menu_window.geometry("400x400")

        tk.Label(menu_window, text="Menú de Neo4j", font=("Helvetica", 14), bg="#35313b", fg="white").pack(pady=10)

        # Botón para subir el grafo
        tk.Button(
            menu_window,
            text="Subir grafo a Neo4j",
            command=lambda: self.upload_graph_to_neo4j(neo4j_manager),
            bg="#5a5566",
            fg="white",
            font=("Helvetica", 12),
            width=30,
            height=2
        ).pack(pady=10)

        # Botón para descargar el grafo
        tk.Button(
            menu_window,
            text="Descargar grafo desde Neo4j",
            command=lambda: self.download_graph_from_neo4j(neo4j_manager),
            bg="#5a5566",
            fg="white",
            font=("Helvetica", 12),
            width=30,
            height=2
        ).pack(pady=10)

        # Botón para ejecutar consultas
        tk.Button(
            menu_window,
            text="Ejecutar consulta Cypher",
            command=lambda: self.open_cypher_terminal(neo4j_manager),
            bg="#5a5566",
            fg="white",
            font=("Helvetica", 12),
            width=30,
            height=2
        ).pack(pady=10)


    def upload_graph_to_neo4j(self, neo4j_manager):
        """
        Sube el grafo cargado en la aplicación a Neo4j.
        """
        if not self.graph:
            messagebox.showwarning("Advertencia", "Cargue un grafo primero.")
            return

        try:
            neo4j_manager.clear_database()  # Opcional: Limpia la base de datos
            neo4j_manager.upload_graph(self.graph)
            messagebox.showinfo("Éxito", "Grafo subido a Neo4j con éxito.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo subir el grafo: {e}")

    def download_graph_from_neo4j(self, neo4j_manager):
        """
        Descarga el grafo desde Neo4j y lo carga en la aplicación.
        """
        try:
            self.graph = neo4j_manager.download_graph()
            messagebox.showinfo("Éxito", "Grafo descargado de Neo4j con éxito.")
            # Mostrar información del grafo
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert(tk.END, f"Nodos descargados: {len(self.graph.nodes())}\n")
            self.results_text.insert(tk.END, f"Relaciones descargadas: {len(self.graph.edges())}\n")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo descargar el grafo: {e}")

    def open_cypher_terminal(self, neo4j_manager):
        """
        Abre una terminal para ejecutar consultas Cypher.
        """
        terminal_window = Toplevel(self.root)
        terminal_window.title("Terminal Cypher")
        terminal_window.configure(bg="#35313b")
        terminal_window.geometry("500x400")

        tk.Label(terminal_window, text="Ejecutar Consulta Cypher", font=("Helvetica", 14), bg="#35313b", fg="white").pack(pady=10)

        query_text = tk.Text(terminal_window, height=10, width=60, bg="#2c2a33", fg="white", font=("Consolas", 10))
        query_text.pack(pady=10)

        results_text = tk.Text(terminal_window, height=10, width=60, bg="#2c2a33", fg="white", font=("Consolas", 10))
        results_text.pack(pady=10)

        def execute_query():
            query = query_text.get("1.0", tk.END).strip()
            if not query:
                messagebox.showwarning("Advertencia", "Ingrese una consulta Cypher.")
                return
            try:
                results = neo4j_manager.execute_query(query)
                results_text.delete("1.0", tk.END)
                for record in results:
                    results_text.insert(tk.END, f"{record}\n")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo ejecutar la consulta: {e}")

        tk.Button(
            terminal_window,
            text="Ejecutar Consulta",
            command=execute_query,
            bg="#5a5566",
            fg="white",
            font=("Helvetica", 12),
            width=20,
            height=2
        ).pack(pady=10)


# Iniciar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = GraphVoyagerApp(root)
    root.mainloop()
