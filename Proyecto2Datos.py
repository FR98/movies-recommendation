# Proyecto 2 Estructuras de Datos
# Gian Luca Rivera 18049
# Francisco Rosal 18676
# Programa de recomendacion de peliculas

from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "admin123"))

def deleteLast(tx):
    tx.run("MATCH (n) DETACH DELETE n")

def initTransaction(tx):
    file = open("db.txt", "r", encoding='utf-8')
    datab = file.read()
    tx.run(datab)
    file.close

def userExist(tx, user):
    for result in tx.run("""
        MATCH (user: User) WHERE user.name = $user
        RETURN user.name
    """, user=user):
        userReturned = result["user.name"]
        if (userReturned):
            print("---------------------------")
            print("Welcome " + userReturned)
            return True
        return False

def showMoviesUserLiked(tx, user):
    print("---------------------------")
    for movie in tx.run("""
        MATCH (user:User) WHERE user.name = $user
        MATCH (user) -[:LIKED]-> (movie:Movie)
        RETURN movie.title
    """, user=user):
        print(movie["movie.title"])
    print("---------------------------")

def recommendMeJaccard(tx, user):
    # Hace la busqueda en la base de datos
    for movie in tx.run("""
        MATCH (user:User) WHERE user.name = $user
        MATCH (user) -[:LIKED]-> (movie:Movie)
        MATCH (movie:Movie)-[:IN_GENRE|:ACTED_IN|:PRODUCED|:DIRECTED]-(filtered)<-[:IN_GENRE|:ACTED_IN|:PRODUCED|:DIRECTED]-(recMovie:Movie)
            WHERE NOT EXISTS( (user)-[:LIKED]->(recMovie) )
        WITH movie, recMovie, COUNT(filtered) AS intersection

        MATCH (movie)-[:IN_GENRE|:ACTED_IN|:PRODUCED|:DIRECTED]-(mov)
        WITH movie, recMovie, intersection, COLLECT(mov.name) AS conjunto1
        MATCH (recMovie)-[:IN_GENRE|:ACTED_IN|:PRODUCED|:DIRECTED]-(re)
        WITH movie, recMovie, intersection, conjunto1, COLLECT(re.name) AS conjunto2

        WITH movie, recMovie, intersection, conjunto1, conjunto2, conjunto1 + filter(i IN conjunto2 WHERE NOT i IN conjunto1) AS union
        RETURN movie.title AS YouLike, recMovie.title AS Recommendation, conjunto1 AS Props1, conjunto2 AS Props2,
            ((1.0*intersection) / SIZE(union)) AS JaccardNumber
        ORDER BY JaccardNumber DESC LIMIT 25
    """, user=user):
        # Descubrir como retornar mas elementos
        print(movie["Recommendation"])

def recommendMePriority(tx, user):
    # Hace la busqueda en la base de datos
    for movie in tx.run("""
        MATCH (user:User) WHERE user.name = $user
        MATCH (user) -[:LIKED]-> (movie:Movie)

        MATCH (movie) -[:IN_GENRE]-> (genre:Genre) <-[:IN_GENRE]- (rec:Movie) WHERE NOT EXISTS( (user) -[:LIKED]-> (rec) )
        WITH user, movie, rec, COUNT(genre) AS genreSelection
        MATCH (movie) <-[:ACTED_IN]- (actor:Person) -[:ACTED_IN]-> (rec)
        WITH user, movie, rec, genreSelection, COUNT(actor) AS actorSelection
        MATCH (movie) <-[:PRODUCED]- (productor:Productor) -[:PRODUCED]-> (rec)
        WITH user, movie, rec, genreSelection, actorSelection, COUNT(productor) AS productorSelection
        OPTIONAL MATCH (movie) <-[:DIRECTED]- (director:Person) -[:DIRECTED]-> (rec)
        WITH user, movie, rec, genreSelection, actorSelection, productorSelection, COUNT(director) AS directorSelection

        MATCH (movie) -[:IN_GENRE|:ACTED_IN|:DIRECTED]- (mov)
        WITH user, movie, rec, genreSelection, actorSelection, productorSelection, directorSelection, COLLECT(mov.name) AS conjunto1
        MATCH (rec) -[:IN_GENRE|:ACTED_IN|:DIRECTED]- (re)
        WITH user, movie, rec, genreSelection, actorSelection, productorSelection, directorSelection, conjunto1, COLLECT(re.name) AS conjunto2

        RETURN user.name AS User, rec.title AS Recommendation, rec.year AS Year, conjunto1 AS Props1, conjunto2 AS Props2,
            genreSelection AS GenreMatch, actorSelection AS ActorMatch, productorSelection AS ProductorMatch, directorSelection AS DirectorMatch,
            ((0.5*genreSelection)+(0.25*actorSelection)+(0.25*directorSelection))/(genreSelection+actorSelection+directorSelection) AS MatchScore
        ORDER BY MatchScore DESC LIMIT 25
    """, user=user):
        # Descubrir como retornar mas elementos
        print(movie["Recommendation"])

def addNewMovieLiked(tx, user, movie):
    # Agrega una nueva pelicula y hace los enlaces
    # Leer un api para obtener toda la info de la pelicula?
    print("---------------------------")
    tx.run("""
    MATCH (user:User) WHERE user.name = $user
    MERGE (user) -[:LIKED]-> (m: Movie {title: $movie})
    """, user=user, movie=movie)

def menu():
    return ("""
    -----------------------------
    Menu:
    1. Show movies you liked
    2. Add movie to your list
    3. Recommend me
    4. Salir
    -----------------------------
    """)

print("Welcome to the movie recommender")

with driver.session() as session:
    session.write_transaction(deleteLast)
    session.write_transaction(initTransaction)

session = driver.session()

userEnter = True
while userEnter:
    user = input("Ingrese su nombre de usuario: ")
    exist = session.read_transaction(userExist, user)
    if exist:

        continuar = True
        while continuar:
            print(menu())
            option = input("Option: ")

            if (option == "1"):
                print("Movies "+user+" liked:")
                session.read_transaction(showMoviesUserLiked, user)
            elif (option == "2"):
                newMovie = input("Enter the name of the movie you want to add: ")
                session.write_transaction(addNewMovieLiked, user, newMovie)
            elif (option == "3"):
                #findMovieRelateTo = input("Enter the name of the movie: ")
                session.read_transaction(recommendMeJaccard, user)
                session.read_transaction(recommendMePriority, user)
            elif (option == "4"):
                print("Bye bye")
                continuar = False
                userEnter = False
            else:
                print("Wrong option!")
    else:
        print("User doesnt exist, try again.")
