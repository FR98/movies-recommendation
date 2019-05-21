# Proyecto 2 Estructuras de Datos
# Gian Luca Rivera 18049
# Francisco Rosal 18676
# Programa de recomendacion de peliculas

from neo4j import GraphDatabase
import omdb

# Para usar el API base de datos de peliculas:
# pip install omdb
API_KEY = "3f058774"
omdb.set_default('apikey', API_KEY)

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
        ORDER BY JaccardNumber DESC LIMIT 15
    """, user=user):
        print("Because you like: " + movie["YouLike"] + "\nWe recommend: \t" + movie["Recommendation"] + "\n")

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

        RETURN movie.title AS YouLike, rec.title AS Recommendation, rec.year AS Year, conjunto1 AS Props1, conjunto2 AS Props2,
            genreSelection AS GenreMatch, actorSelection AS ActorMatch, productorSelection AS ProductorMatch, directorSelection AS DirectorMatch,
            ((0.5*genreSelection)+(0.25*actorSelection)+(0.25*directorSelection))/(genreSelection+actorSelection+directorSelection) AS MatchScore
        ORDER BY MatchScore DESC LIMIT 15
    """, user=user):
        print("Because you like: " + movie["YouLike"] + "\nWe recommend: \t" + movie["Recommendation"] + "\n")

def findMovieRelateTo(tx, movie):
    # Hace la busqueda en la base de datos
    for movie in tx.run("""
        MATCH (movie:Movie) WHERE movie.title = $movie
        MATCH (movie:Movie)-[:IN_GENRE|:ACTED_IN|:PRODUCED|:DIRECTED]-(filtered)<-[:IN_GENRE|:ACTED_IN|:PRODUCED|:DIRECTED]-(recMovie:Movie)
        WITH movie, recMovie, COUNT(filtered) AS intersection

        MATCH (movie)-[:IN_GENRE|:ACTED_IN|:PRODUCED|:DIRECTED]-(mov)
        WITH movie, recMovie, intersection, COLLECT(mov.name) AS conjunto1
        MATCH (recMovie)-[:IN_GENRE|:ACTED_IN|:PRODUCED|:DIRECTED]-(re)
        WITH movie, recMovie, intersection, conjunto1, COLLECT(re.name) AS conjunto2

        WITH movie, recMovie, intersection, conjunto1, conjunto2, conjunto1 + filter(i IN conjunto2 WHERE NOT i IN conjunto1) AS union
        RETURN movie.title AS YouLike, recMovie.title AS Recommendation, conjunto1 AS Props1, conjunto2 AS Props2,
            ((1.0*intersection) / SIZE(union)) AS JaccardNumber
        ORDER BY JaccardNumber DESC LIMIT 15
    """, movie=movie):
        print(movie["Recommendation"])

def addNewMovieLiked(tx, user, movieInfo):
    # Agrega una nueva pelicula y hace los enlaces
    movieTitle = movieInfo["title"]
    if movieInfo["year"]:
        movieYear = movieInfo["year"]
    else:
        movieYear = "NaN"

    if movieInfo["director"]:
        movieDirector = movieInfo["director"]
    else:
        movieDirector = "NaN"

    if movieInfo["actors"]:
        movieActor = movieInfo["actors"]
    else:
        movieActor = "NaN"

    if movieInfo["production"]:
        movieProducer = movieInfo["production"]
    else:
        movieProducer = "NaN"

    if movieInfo["genre"]:
        movieGenre = movieInfo["genre"]
    else:
        movieGenre = "NaN"

    print("---------------------------")

    for res1 in tx.run("""
        MATCH (movie:Movie) WHERE movie.title = $movie
        RETURN movie
    """, movie=movieTitle):
        if res1["movie"]:
            tx.run("""
                MATCH (user:User) WHERE user.name = $user
                MATCH (movie:Movie) WHERE movie.title = $movie
                MERGE (user) -[:LIKED]-> (movie)
            """, user=user, movie=movieTitle)
        else:
            tx.run("""
                MATCH (user:User) WHERE user.name = $user
                MERGE (user) -[:LIKED]-> (m: Movie {title: $movie, year: $year})
            """, user=user, movie=movieTitle, year=movieYear)

    directors = movieDirector.split(", ")
    for d in directors:
        for res2 in tx.run("""
            MATCH (director:Person) WHERE director.name = $name
            RETURN director
        """, name=d):
            if res2["director"]:
                tx.run("""
                    MATCH (movie:Movie) WHERE movie.title = $movie
                    MATCH (director:Person) WHERE director.name = $name
                    MERGE (director) -[:DIRECTED]-> (movie)
                """, name=d, movie=movieTitle)
            else:
                tx.run("""
                    MATCH (movie:Movie) WHERE movie.title = $movie
                    MERGE (movie) <-[:DIRECTED]- (:Person {name: $name})
                """, name=d, movie=movieTitle)

    actors = movieActor.split(", ")
    for a in actors:
        for res3 in tx.run("""
            MATCH (actor:Person) WHERE actor.name = $name
            RETURN actor
        """, name=a):
            if res3["actor"]:
                tx.run("""
                    MATCH (movie:Movie) WHERE movie.title = $movie
                    MATCH (actor:Person) WHERE actor.name = $name
                    MERGE (actor) -[:ACTED_IN]-> (movie)
                """, name=a, movie=movieTitle)
            else:
                tx.run("""
                    MATCH (movie:Movie) WHERE movie.title = $movie
                    MERGE (movie) <-[:ACTED_IN]- (:Person {name: $name})
                """, name=a, movie=movieTitle)

    productors = movieProducer.split(", ")
    for p in productors:
        for res4 in tx.run("""
            MATCH (productor:Productor) WHERE productor.name = $name
            RETURN productor
        """, name=p):
            if res4["productor"]:
                tx.run("""
                    MATCH (movie:Movie) WHERE movie.title = $movie
                    MATCH (productor:Productor) WHERE productor.name = $name
                    MERGE (productor) -[:PRODUCED]-> (movie)
                """, name=p, movie=movieTitle)
            else:
                tx.run("""
                    MATCH (movie:Movie) WHERE movie.title = $movie
                    MERGE (movie) <-[:PRODUCED]- (:Productor {name: $name})
                """, name=p, movie=movieTitle)

    genres = movieGenre.split(", ")
    for g in genres:
        for res5 in tx.run("""
            MATCH (genre:Genre) WHERE genre.name = $name
            RETURN genre
        """, name=g):
            if res5["genre"]:
                tx.run("""
                    MATCH (movie:Movie) WHERE movie.title = $movie
                    MATCH (genre:Genre) WHERE genre.name = $name
                    MERGE (genre) <-[:IN_GENRE]- (movie)
                """, name=g, movie=movieTitle)
            else:
                tx.run("""
                    MATCH (movie:Movie) WHERE movie.title = $movie
                    MERGE (movie) -[:IN_GENRE]-> (:Genre {name: $name})
                """, name=g, movie=movieTitle)


def menu():
    return ("""
    -----------------------------
    Menu:
    1. Show movies you liked
    2. Add movie to your list
    3. Recommend me
    4. Find movie relate to
    5. Salir
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
                res = omdb.get(title=newMovie)
                if res:
                    que1 = input("Is this your movie? \t" + res["title"] + "\n (yes/no): ")
                    if que1 == "yes":
                        session.write_transaction(addNewMovieLiked, user, res)
                    else:
                        print("Sorry, maybe it's not its name... try again :)")
                else:
                    print("Sorry, maybe it's not its name... try again :)")
            elif (option == "3"):
                session.read_transaction(recommendMeJaccard, user)
                session.read_transaction(recommendMePriority, user)
            elif (option == "4"):
                movie = input("Enter the name of the movie: ")
                print("---------------------------")
                print("Movies related to " + movie)
                print("---------------------------")
                session.read_transaction(findMovieRelateTo, movie)
            elif (option == "5"):
                print("Bye bye")
                continuar = False
                userEnter = False
            else:
                print("Wrong option!")
    else:
        print("User doesnt exist, try again.")
