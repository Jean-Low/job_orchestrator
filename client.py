print("Im a client but im not ready, read the REST readme and use it there for now")

import json
import requests as req

url = "http://127.0.0.1:5000/"

r = req.get(url)
print(r.text)