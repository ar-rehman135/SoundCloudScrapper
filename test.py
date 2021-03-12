import re
import requests
import json
import time
import pandas as pd
import random
import portalocker
import logging
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.chrome.options import Options


# from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
# # from http_request_randomizer.requests.useragent.userAgent import logger
# from http_request_randomizer.requests.parsers.PremProxyParser import logger as logPrem
# from http_request_randomizer.requests.parsers.js.UnPacker import logger as logUnPacker


LOGGER.setLevel(logging.WARNING)
# logger.setLevel(logging.WARNING)
# logPrem.setLevel(logging.CRITICAL)
# logUnPacker.setLevel(logging.CRITICAL)


options = Options()
options.headless = True
options.add_argument("--window-size=2000,5000")
options.add_argument("--disable-logging")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
DRIVER_PATH = 'chromedriver.exe'
# req_proxy = RequestProxy()
# proxies = req_proxy.get_proxy_list()
# PROXY = proxies[random.randint(0, 300)].get_address()

isProxy = 'y'#input('Do you want to run on proxy server (y/n)? ')
if isProxy == 'y' or isProxy == 'Y':
    proxy_ip = "proxy-server.scraperapi.com" #input("Enter Ip Address: ")
    proxy_port = "8001" #input("Enter Port: ")
    proxy_username = "scraperapi" #input("Enter Username: ")
    proxy_password = "c3b55c1f2a08bda66509951be3488fc9" #input("Enter Password: ")

    # PROXY = proxy_username + ":" + proxy_password + "@" + proxy_ip + ':' + proxy_port
    # PROXY = 'scraperapi:c3b55c1f2a08bda66509951be3488fc9@proxy-server.scraperapi.com:8001'
    # print("PROXY", PROXY)
    # proxy = Proxy()
    #
    # proxy.proxy_type = ProxyType.MANUAL
    # proxy.http_proxy = PROXY
    # proxy.ssl_proxy = PROXY
    # proxy.ftp_proxy = PROXY
    #
    # capabilities = webdriver.DesiredCapabilities.CHROME
    # proxy.add_to_capabilities(capabilities)

    # PROXY = proxy_ip + ':' + proxy_port
    # options.add_argument("proxy-server={}".format(PROXY))


# driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH, service_log_path="NULL")

proxies = {
  "http": "http://scraperapi:c3b55c1f2a08bda66509951be3488fc9@proxy-server.scraperapi.com:8001",
  "https": "http://scraperapi:c3b55c1f2a08bda66509951be3488fc9@proxy-server.scraperapi.com:8001"
}
initialurl = 'https://api-v2.soundcloud.com/search/users?q=rapper&sc_a_id=947f59c5-40ea-4f14-bbed-9887e172fbd5&variant_ids=2077%2C2200&facet=place&user_id=825873-12912-268615-711068&client_id=kI6aD0LqK9uSmqaqAxmm1f2w9UVidheL&limit=100&offset=0&linked_partitioning=1&app_version=1613488296&app_locale=en'
url = 'https://www.expressvpn.com/what-is-my-ip'
PROXY = {
    "http": "http://103.119.244.10:55207",
    "https": "http://103.119.244.10:55207"
}

r = requests.get(initialurl, proxies=PROXY)

print(r.text)
# driver.get('https://www.expressvpn.com/what-is-my-ip')
# time.sleep(10)
# driver.save_screenshot('ss1.png')

# driver.quit()
