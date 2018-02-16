import requests
import json

urls1 = "https://www.frederikal.dk/bp/server1"
urls2 = "https://www.frederikal.dk/bp/server2"

data = {'name': 'a', 'value': 5}

resp = requests.request("post", urls1, json=data)
print(resp.text)