import os
import re
import zipfile
import random

import requests
import json
import time
import pandas as pd
import portalocker
import logging
from selenium import webdriver
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.chrome.options import Options


LOGGER.setLevel(logging.WARNING)
options = Options()
options.headless = True
options.add_argument("--window-size=5000,15000")
options.add_argument("--disable-logging")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
DRIVER_PATH = 'chromedriver.exe'


isProxy = input('Do you want to run on proxy server (y/n)? ')
def get_chromedriver():
    try:
        PROXY = ''
        if os.path.exists('proxy.config.json'):
            with open('proxy.config.json') as fd:
                obj = json.load(fd)
                # print(obj)
                excludes = obj['excludes']
                if isProxy == 'y' or isProxy == 'Y':
                    if not obj['proxy_ip'] == '':
                        PROXY = obj['proxy_ip']
                        if not obj['proxy_port'] == '':
                            if not len(obj['proxy_ip']) == len(obj['proxy_port']):
                                print('Add Equal Number of Ip Address and Ports')
                            else:
                                random_num = random.randint(0, (len(obj['proxy_ip']) - 1))
                                PROXY = obj['proxy_ip'][random_num] + ':' + obj['proxy_port'][random_num]
                                # print(PROXY)

                                if obj['proxy_username']:
                                    PROXY = obj['proxy_username'] + ':' + obj['proxy_password'] + '@' + PROXY
                                    print("PROXY", PROXY)
                                    PROXY = 'https://' + PROXY
                                    manifest_json = """
                                    {
                                        "version": "1.0.0",
                                        "manifest_version": 2,
                                        "name": "Chrome Proxy",
                                        "permissions": [
                                            "proxy",
                                            "tabs",
                                            "unlimitedStorage",
                                            "storage",
                                            "<all_urls>",
                                            "webRequest",
                                            "webRequestBlocking"
                                        ],
                                        "background": {
                                            "scripts": ["background.js"]
                                        },
                                        "minimum_chrome_version":"22.0.0"
                                    }
                                    """

                                    background_js = """
                                    var config = {
                                            mode: "fixed_servers",
                                            rules: {
                                              singleProxy: {
                                                scheme: "http",
                                                host: "%s",
                                                port: parseInt(%s)
                                              },
                                              bypassList: ["localhost"]
                                            }
                                          };
                
                                    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
                
                                    function callbackFn(details) {
                                        return {
                                            authCredentials: {
                                                username: "%s",
                                                password: "%s"
                                            }
                                        };
                                    }
                
                                    chrome.webRequest.onAuthRequired.addListener(
                                                callbackFn,
                                                {urls: ["<all_urls>"]},
                                                ['blocking']
                                    );
                                    """ % (obj['proxy_ip'], obj['proxy_port'], obj['proxy_username'], obj['proxy_password'])
                                    pluginfile = 'proxy_auth_plugin.zip'

                                    with zipfile.ZipFile(pluginfile, 'w') as zp:
                                        zp.writestr("manifest.json", manifest_json)
                                        zp.writestr("background.js", background_js)
                                    options.add_extension(pluginfile)
                                    options.headless = False
                                    driver = webdriver.Chrome(
                                        executable_path=DRIVER_PATH,
                                        options=options, service_log_path="NULL")
                                else:
                                    options.add_argument("proxy-server={}".format(PROXY))
                                    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH, service_log_path="NULL")

                    else:
                        driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH, service_log_path="NULL")
                else:
                    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH, service_log_path="NULL")
        else:
            driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH, service_log_path="NULL")
        return driver, PROXY, excludes
    except Exception as ex:
        print(ex)


driver, PROXY, excludes = get_chromedriver()

initialurl = 'https://api-v2.soundcloud.com/search/users?q=rapper&sc_a_id=577a677d42d8462a4c35f86450c82c61d176ba95&variant_ids=2077&facet=place&user_id=825873-12912-268615-711068&client_id=OBhq4Cf6jGxc2cbaKvzxJX8QQLKXEryc&limit=100&offset=<offset>&linked_partitioning=1&app_version=1616065176&app_locale=en'

def sleep_and_find(find_sel):
    for i in range(20):
        try:
            data = driver.find_element_by_xpath(find_sel)
            return data
        except:
            time.sleep(1)

def findByXPATH(elem):
    try:
        ele = driver.find_element_by_xpath(elem)
    except:
        ele = type('Expando', (object,), {})()
        ele.text = ""
    return ele

def replace_all(text):
    text = re.sub(r'\bOfficial\b', "", text)
    text = re.sub(r'\bThe\b', "", text)
    text = re.sub(r'\bthe\b', "", text)
    text = re.sub(r'\bRapper\b', "", text)
    text = re.sub(r'\brapper\b', "", text)
    text = re.sub(r'\bda\b', "", text)
    text = re.sub(r'\btha\b', "", text)
    text = re.sub(r'\bmusic\b', "", text)
    text = re.sub(r'\bFeat\b', "", text)

    return text

def main():
    try:
        print("10000 entries found for scraping")
        entries_start = input("Enter Start Number: ")
        entries = input("Enter Number of entries you want to scrap: ")
        #excludes = ['DJ', 'repost', 'management', 'group', 'agency', 'singer', 'beat', 'producer', 'prod by']

        print("Data Scrapping...")

        entry_count = int(entries) / 100

        if entry_count < 1:
            entry_count = 1

        rapper_data = []
        filename = "SoundCloudRapperData.csv"
        if not os.path.exists(filename):
            count = 0
        else:
            count = 1
        global driver, PROXY, excludes
        print("PROXY", PROXY)
        proxies = {
            "http": "http://" + PROXY,
            "https": "http://" + PROXY
        }

        with open(filename, 'a') as file:
            portalocker.lock(file, portalocker.LOCK_EX)

            for n in range(round(entry_count)):
                url = initialurl.replace('<offset>', str((n * 100)+int(entries_start)))
                try:
                    data = requests.get(url, proxies=proxies)
                except:
                    data = requests.get(url)
                dataStr = data.content.decode('utf-8')
                dataObj = json.loads(dataStr)
                # print(dataObj)
                # print(driver)

                total_results = dataObj['total_results']
                for i in range(len(dataObj['collection'])):
                    print(i)
                    permalink = dataObj['collection'][i]['permalink']
                    try:
                        driver.get("https://soundcloud.com/" + permalink + "/tracks")
                    except:
                        driver, PROXY, excludes = get_chromedriver()
                        driver.get("https://soundcloud.com/" + permalink + "/tracks")

                    bio = sleep_and_find('//*[@id="content"]/div/div[4]/div[2]/div/article[1]')
                    try:
                        show_more = findByXPATH('//*[@id="content"]/div/div[4]/div[2]/div/article[1]/div[1]/div/a')
                        show_more.click()
                    except:
                        pass

                    try:
                        bio = bio.text
                    except:
                        bio = ''
                        pass

                    excluded_word = False
                    # if re.search(r'\brapper\b', bio, re.IGNORECASE):
                    for exclude in excludes:
                        if re.search(exclude, bio, re.IGNORECASE):
                            excluded_word = True
                            break
                    if not excluded_word:
                        email = re.search(r'\S+@\S+\.\S+', bio, re.IGNORECASE)

                        IG_username, IG_URL = None, None
                        if re.search(r'\binstagram\b', bio, re.IGNORECASE):
                            web_profiles = driver.find_element_by_xpath('//*[@id="content"]/div/div[4]/div[2]/div/article[1]/div[2]/ul')
                            web_profiles_list = web_profiles.find_elements_by_tag_name('li')
                            for i in range(len(web_profiles_list)):
                                href = driver.find_element_by_xpath('//*[@id="content"]/div/div[4]/div[2]/div/article[1]/div[2]/ul/li[' + str((i+1)) + ']/div/a').get_attribute('href')
                                if 'instagram' in href:
                                    IG_username = re.search(r'%2F(.*?)%2F', href)
                                    print(IG_username)
                                    IG_URL = "https://www.instagram.com/" + IG_username.group(1)

                        if email is not None or IG_username is not None:
                            username = dataObj['collection'][i]['username']
                            permalink_url = dataObj['collection'][i]['permalink_url']
                            full_name = dataObj['collection'][i]['full_name']
                            location = str(dataObj['collection'][i]['city']) + " " + str(dataObj['collection'][i]['country_code'])
                            name_title = sleep_and_find('//*[@id="content"]/div/div[4]/div[1]/div/div[2]/div/ul/li[1]/div/div/div[2]/div[1]/div/div/div[2]/a/span')

                            try:
                                name_title = name_title.text
                            except:
                                name_title = ''

                            full_name2 = replace_all(full_name)
                            try:
                                full_name2 = full_name2.split('(')[0]
                            except:
                                pass
                            try:
                                full_name2 = full_name2.split('[')[0]
                            except:
                                pass
                            try:
                                full_name2 = full_name2.split('|')[0]
                            except:
                                pass

                            if '- ' in name_title:
                                rapper_name = name_title.split('-')[0]
                                rapper_name = replace_all(rapper_name)
                                try:
                                    rapper_name = rapper_name.split('x ')[0]
                                except:
                                    pass
                                try:
                                    rapper_name = rapper_name.split(',')[0]
                                except:
                                    pass
                                try:
                                    rapper_name = rapper_name.split('feat')[0]
                                except:
                                    pass
                                try:
                                    rapper_name = rapper_name.split('Feat')[0]
                                except:
                                    pass
                                try:
                                    rapper_name = rapper_name.split('prod')[0]
                                except:
                                    pass
                                try:
                                    rapper_name = rapper_name.split('(')[0]
                                except:
                                    pass
                                try:
                                    rapper_name = rapper_name.split('and')[0]
                                except:
                                    pass
                                try:
                                    rapper_name = rapper_name.split('&')[0]
                                except:
                                    pass
                                try:
                                    rapper_name = rapper_name.split('+')[0]
                                except:
                                    pass
                                try:
                                    rapper_name = rapper_name.split('[')[0]
                                except:
                                    pass
                                try:
                                    rapper_name = rapper_name.split('|')[0]
                                except:
                                    pass





                                try:
                                    song_title = name_title.split('-')[1] + name_title.split('-')[2]
                                except:
                                    song_title = name_title.split('-')[1]
                                song_title_full = song_title

                                try:
                                    song_title = song_title.split('(')[0]
                                except:
                                    pass
                                try:
                                    song_title = song_title.split('[')[0]
                                except:
                                    pass
                                try:
                                    song_title = song_title.split('feat')[0]
                                except:
                                    pass
                                try:
                                    song_title = song_title.split('Feat')[0]
                                except:
                                    pass

                            else:
                                rapper_name = replace_all(username)
                                try:
                                    rapper_name = rapper_name.split('(')[0]
                                except:
                                    pass
                                try:
                                    rapper_name = rapper_name.split('[')[0]
                                except:
                                    pass
                                try:
                                    rapper_name = rapper_name.split('|')[0]
                                except:
                                    pass


                                song_title_full = name_title
                                try:
                                    song_title = name_title.split('(')[0]
                                except:
                                    pass
                                try:
                                    song_title = song_title.split('[')[0]
                                except:
                                    pass
                                try:
                                    song_title = song_title.split('Feat')[0]
                                except:
                                    pass
                                try:
                                    song_title = song_title.split('feat')[0]
                                except:
                                    pass
                                try:
                                    song_title = song_title.split('ft')[0]
                                except:
                                    pass
                                try:
                                    song_title = song_title.split('Ft')[0]
                                except:
                                    pass

                            if full_name2 == '':
                                full_name2 = rapper_name.strip()

                            song_title = song_title.strip()
                            if song_title.isascii():
                                song_title = song_title
                            else:
                                song_title = ''

                            print(email.group(0))
                            print(IG_username.group(1))

                            rapper_list = [username, rapper_name.strip(), full_name2, location, permalink_url,
                                           email.group(0), song_title, song_title_full, IG_URL, IG_username.group(1)]
                            rapper_data.append(rapper_list)

                if len(rapper_data) > 0:
                    count += 1
                    portalocker.unlock(file)
                    rapper_data_df = pd.DataFrame(rapper_data)
                    rapper_data_df.columns = ['Username', 'FullName', 'FullName2', 'Location', 'RapperURL',
                                              'Email', 'SongTitle', 'SongTitleFull', 'InstagramURL', 'InstagramUserName']
                    if count == 1:
                        rapper_data_df.to_csv(filename, mode='a', index=False, header=True)
                    else:
                        rapper_data_df.to_csv(filename, mode='a', index=False, header=False)

                    print(str((n + 1) * 100) + " Entries Scrapped Successfully and saved into " + filename)
                    rapper_data = []
                else:
                    print("No Rapper Found in 100 entries")

                driver, PROXY, excludes = get_chromedriver()
        print('All data Scrapped Successfully and saved in File ' + filename)
        k = input("******* press any key to exit *******")
    except Exception as ex:
        print(ex, 'Please first close the file.')
        k = input("******* press any key to exit *******")


if __name__ == "__main__":
    main()
    driver.quit()