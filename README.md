# Graph Voyager

Graph Voyager es una herramienta para el análisis y gestión de grafos, diseñada para combinar la potencia de Python y la base de datos orientada a grafos Neo4j. Este proyecto permite realizar tareas como la carga y exportación de grafos, el cálculo de métricas estructurales, la visualización de redes y la ejecución de consultas personalizadas en Neo4j.

## Características

- **Carga de grafos** en formatos estándar:
  - CSV
  - GML
  - GraphML
  - Edgelist
- **Cálculo de métricas estructurales**:
  - Centralidad (Betweenness, Closeness, Eigenvector)
  - Coeficientes de clustering
  - Conectividad
  - Distribución de grados
- **Visualización de grafos** usando Matplotlib.
- **Exportación de métricas** a archivos CSV.
- **Integración con Neo4j**:
  - Subida y descarga de grafos.
  - Ejecución de consultas personalizadas con Cypher.

## Requisitos

- Python 3.8 o superior.
- Neo4j Desktop (versión 5 o superior).
- Dependencias de Python (ver [requirements.txt](requirements.txt)).

## Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/pbarbadol/Graph-Voyager.git
   cd Graph-Voyager
   ```

2. Instala las dependencias del proyecto:
   ```bash
   pip install -r requirements.txt
   ```

3. Configura Neo4j:
   - Inicia el servidor Neo4j en tu máquina local.
   - Configura las credenciales en la aplicación (por defecto: usuario `neo4j`, contraseña `12345678`).

## Uso

1. Ejecuta la aplicación principal:
   ```bash
   python src/graph_voyager_gui.py
   ```

2. Sigue las instrucciones en la interfaz gráfica para:
   - Cargar un grafo desde un archivo.
   - Calcular métricas del grafo.
   - Visualizar el grafo.
   - Exportar los resultados o interactuar con Neo4j.
