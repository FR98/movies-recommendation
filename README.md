# Proyecto2Datos

Este proyecto es un sistema de recomendacion de peliculas a base de peliculas que ya le gustan al usuario. El mismo implementa dos algoritmos: el primero se basa en el algoritmo de Jaccard y el segundo es un sistema de prioridad que le da un valor a la cantidad de similitudes entre dos peliculas (revisa todos los nodos de cada pelicula). Tambien, el proyecto hace uso de un api llamada OMDb extraida de: http://www.omdbapi.com por si se quiere añadir una pelicula a las favoritas de un usuario y esta no se encuentra en la base de datos inicial que esta creada en Neo4j.

El proyecto esta formado por lo siguiente:
- Una base de datos basada en nodos (Neo4j) que inicialmente tiene:
  * 20 User
  * 89 Movie
  * 463 Person (Actors and Directors)
  * 21 Genre
  * 83 Productor
  * Para un total de 676 nodos y 1260 relaciones.
- Algoritmo Jaccard: Esta basado en el indice de Jaccard que compara dos grupos de elementos con el calculo de interseccion dividido la union de los grupos. Esta escrito totalmente en cypher.
- Algoritmo de prioridad: le da un valor a la cantidad de similitudes entre dos peliculas siendo estos valores:
  * Genero * 0.5
  * Actores * 0.25
  * Director * 0.25
  La suma de estas multiplicaciones se divide dentro de la suma de las cantidades de coincidencias entre ambas peliculas.

En la carpeta que contiene todos los archivos se puede encontrar lo siguiente:
- Un documento PDF explicando el proyecto por medio de la metodologia de design thinking. (Primera parte.pdf)
- Un documento de algortimo descriptivo que explica los algoritmos del programa por medio de cypher (algoritmoDescriptivo.txt)
- Una imagen png que explica la relacion entre los nodos de la base de datos basada en nodos
- Un archivo cypher que contiene la inicializacion de la base de datos (db.cypher)
- Una carpeta Testing en donde estan las encuestas realizadas por medio de design thinking
- Un archivo python que contiene todo el codigo del programa (Proyecto2Datos.py)

Para instalar este programa se debe:
1. Instalar Neo4j por medio de la terminal (pip install neo4j)
2. Instalar el api OMDb por medio de la terminal (pip install omdb)
3. Crear la base de datos en la aplicacion de Neo4j Desktop y colocarle la contraseña admin123 o bien colcarle la deseada y cambiarla en el archivo de codigo (Proyecto2Datos.py) en la linea 14.

Para ejecutar el programa se debe:
1. Ingresar a la terminal o cmd
2. Dirigirse a la carpeta en donde se encuentra el Proyecto (por medio de cd)
3. Entrar a la carpeta del proyecto (cd Proyecto2Datos)
4. Escribir "python Proyecto2Datos.py"
