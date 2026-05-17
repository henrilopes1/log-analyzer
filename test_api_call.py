import requests
import json
files = {'firewall_log': open('data/sample_firewall.csv', 'rb'), 'auth_log': open('data/sample_auth.csv', 'rb')}
r = requests.post('http://127.0.0.1:8000/analyze/', files=files)
print(json.dumps(r.json(), indent=2))
