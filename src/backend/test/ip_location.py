import requests
import json
from concurrent.futures import ThreadPoolExecutor
import time


def get_country(ip):
    url = f'http://ipinfo.io/{ip}/json'
    response = requests.get(url)
    data = json.loads(response.text)
    return data['country'], ip

futures = list()
start = time.time()
with ThreadPoolExecutor(max_workers=500) as exc:
    for peer in peers:
        ip, port = peer 
        futures.append(exc.submit(get_country, ip))
    exc.shutdown(wait=True)

for future in futures:
    print(future.result())