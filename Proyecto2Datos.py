# Proyecto 2 Estructuras de Datos
# Gian Luca Rivera 1804
# Francisco Rosal 18676
# Programa de recomendacion de peliculas

from neo4j.v1 import GraphDatabase, basic_auth

class DataBase(object):

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def print_greeting(self, message):
        with self._driver.session() as session:
            greeting = session.write_transaction(self._create_and_return_greeting, message)
            print(greeting)

    @staticmethod
    def _create_and_return_greeting(tx, message):
        result = tx.run("CREATE (a:Greeting) "
                        "SET a.message = $message "
                        "RETURN a.message + ', from node ' + id(a)", message=message)
        return result.single()[0]


# ----------------------------------------------

# driver = GraphDatabase.driver(
#     "bolt://52.91.116.38:38229",
#     auth=basic_auth("neo4j", "frame-partners-staplers"))
# session = driver.session()
#
# cypher_query = '''
# MATCH (n)
# RETURN id(n) AS id
# LIMIT $limit
# '''
#
# results = session.run(cypher_query,
#   parameters={"limit": 10})
#
# for record in results:
#   print(record['id'])
