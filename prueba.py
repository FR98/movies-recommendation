import requests
import omdb

API_KEY = "3f058774"
omdb.set_default('apikey', API_KEY)
res = omdb.get(title="Avengers")

#client = omdb.OMDBClient(apikey=API_KEY)
#res = client.get(title='Avengers')
# print(res)

res = requests.Session().get('http://www.omdbapi.com', apikey=API_KEY, title="Avengers")
print(res)
