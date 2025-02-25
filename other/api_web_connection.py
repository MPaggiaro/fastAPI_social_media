import requests
import json

response_nw = requests.get("http://api.open-notify.org/this-api-doesnt-exist")
print(response_nw.status_code)

response = requests.get("https://www.google.com")
print(response.status_code)
print(response.text)