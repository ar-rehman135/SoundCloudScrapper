import requests

proxies = {
  "http": "http://scraperapi:c3b55c1f2a08bda66509951be3488fc9@proxy-server.scraperapi.com:8001",
  "https": "http://scraperapi:c3b55c1f2a08bda66509951be3488fc9@proxy-server.scraperapi.com:8001"
}


initialurl = 'https://api-v2.soundcloud.com/search/users?q=rapper&sc_a_id=947f59c5-40ea-4f14-bbed-9887e172fbd5&variant_ids=2077%2C2200&facet=place&user_id=825873-12912-268615-711068&client_id=kI6aD0LqK9uSmqaqAxmm1f2w9UVidheL&limit=100&offset=0&linked_partitioning=1&app_version=1613488296&app_locale=en'
url = 'https://www.expressvpn.com/what-is-my-ip'

PROXY = {
    "http": "http://134.209.29.120:8080",
    "https": "http://134.209.29.120:8080",
}

r = requests.get(initialurl, proxies=PROXY)

print(r.text)

