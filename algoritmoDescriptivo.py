Algoritmo de recomendacion:

Nuestro algortimo estará basado en Content-Based Filtering, en el cual el usuario escoge 
peliculas que le gusten y a partir del contenido de la informacion se recomiendan otras peliculas.

Se buscaran similitudes basada en generos segun las peliculas ya vistas por el usuario
ya que es lo que mayor afecta en la decision de las personas al buscar una pelicula. 
Al filtrar por genero se obtendra un numero que indica la cantidad de similitudes existentes con las peliculas de gusto del usuario.
Se hace igualmente con los actores, productora, calificacion, y director, reduciendoce cada vez mas la cantidad de opciones.
Se muestran los valores en comun de cada conjunto por separado.
Al finalizar se obtiene el puntaje de coincidencia haciendo una suma de los valores obtenidos, cada uno multiplicado por un numero 
el cual es la prioridad que se le da a ese valor, a esta suma se le divide la suma de los valores obtenidos.
Se ordena la lista obtenida por ese puntaje de coincidencia y se retorna.

# Algoritmo
MATCH (u:User {name: "User name"})-[r:LIKED]->(m:Movie)

MATCH (m)-[:IN_GENRE]->(g:Genre)<-[:IN_GENRE]-(rec:Movie) WHERE NOT EXISTS( (u)-[:LIKED]->(rec) )
WITH u, m, rec, COUNT(g) AS genreSelection
MATCH (m)<-[:ACTED_IN]-(a:Actor)-[:ACTED_IN]->(rec) 
WITH u, m, rec, genreSelection, COUNT(a) AS actorSelection
OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Director)-[:DIRECTED]->(rec) 
WITH u, m, rec, genreSelection, actorSelection, COUNT(d) AS directorSelection

MATCH (m)-[:IN_GENRE|:ACTED_IN|:DIRECTED]-(mo)
WITH u, m, rec, genreSelection, actorSelection, directorSelection, COLLECT(mo.name) AS conjunto1
MATCH (rec)-[:IN_GENRE|:ACTED_IN|:DIRECTED]-(re)
WITH u, m, rec, genreSelection, actorSelection, directorSelection, conjunto1, COLLECT(re.name) AS conjunto2

RETURN u.name AS User, rec.title AS Recommendation, rec.year AS Year, conjunto1, conjunto2, genreSelection, actorSelection, directorSelection, ((0.5*genreSelection)+(0.25*actorSelection)+(0.25*directorSelection))/(genreSelection+actorSelection+directorSelection) AS score 
ORDER BY score DESC LIMIT 50


Se utilizara el indice de Jaccard que es un numero entre 0 y 1 que indica la similitud de 
dos conjuntos. Este se calcula dividiendo el tamaño de la intersección de dos conjuntos por la unión 
de los dos conjuntos. Para esto se obtiene las peliculas de agrado de un usuario y se compara con todas
las peliculas para obtener las que tienen las mismas propiedades; a este resultado se le conoce como intersección
de dos conjuntos. Se muestran los valores en comun de cada conjunto por separado. Y luego se obtiene la union de estos
conjuntos que es la suma del conjunto 1 con los elementos del conjunto 2 que no tiene el conjunto 1. Se calcula el
indice de Jaccard y se ordena por este.

# Algoritmo
MATCH (u:User {name: "User name"})-[r:LIKED]->(m:Movie)
MATCH (m:Movie)-[:IN_GENRE|:ACTED_IN|:DIRECTED]-(filtered)<-[:IN_GENRE|:ACTED_IN|:DIRECTED]-(rec:Movie) WHERE NOT EXISTS( (u)-[:LIKED]->(rec) )
WITH m, rec, COUNT(filtered) AS intersection

MATCH (m)-[:IN_GENRE|:ACTED_IN|:DIRECTED]-(mo)
WITH m, rec, intersection, COLLECT(mo.name) AS conjunto1
MATCH (rec)-[:IN_GENRE|:ACTED_IN|:DIRECTED]-(re)
WITH m, rec, intersection, conjunto1, COLLECT(re.name) AS conjunto2

WITH m, rec, intersection, conjunto1, conjunto2, conjunto1 + filter(x IN conjunto2 WHERE NOT x IN conjunto1) AS union
RETURN m.title, rec.title, conjunto1, conjunto2, ((1.0*intersection) / SIZE(union)) AS jaccard ORDER BY jaccard DESC LIMIT 50
