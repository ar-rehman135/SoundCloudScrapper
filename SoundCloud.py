import os
import random
import re
import zipfile

from bs4 import BeautifulSoup as bs

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

initialurl = 'https://api-v2.soundcloud.com/search/users?q=rapper&sc_a_id=577a677d42d8462a4c35f86450c82c61d176ba95&variant_ids=2077&facet=place&user_id=825873-12912-268615-711068&client_id=OBhq4Cf6jGxc2cbaKvzxJX8QQLKXEryc&limit=10&offset=<offset>&linked_partitioning=1&app_version=1616065176&app_locale=en'

def get_excludes():
    excludes = ['DJ', 'repost', 'management', 'group', 'agency', 'singer', 'beat', 'producer', 'prod by']
    try:
        if os.path.exists('proxy.exclude.json'):
            with open('proxy.exclude.json') as fd:
                obj = json.loads(fd.read())
                excludes = obj['excludes']
                return excludes
    except Exception as ex:
        print(ex)
    return excludes
def sleep_and_find(find_sel, driver):
    for i in range(20):
        try:
            data = driver.find_element_by_xpath(find_sel)
            return data
        except:
            time.sleep(1)

def findByXPATH(elem, driver):
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

def get_chromedriver():
    try:
        PROXY = ''
        totalProxies = 0
        if os.path.exists('proxy.config.json'):
            with open('proxy.config.json') as fd:
                obj = json.load(fd)
                if not obj['proxy_ip'] == '':
                    PROXY = obj['proxy_ip']
                    if not obj['proxy_port'] == '':
                        if not len(obj['proxy_ip']) == len(obj['proxy_port']):
                            print('Add Equal Number of Ip Address and Ports')
                        else:
                            random_num = random.randint(0, (len(obj['proxy_ip']) - 1))
                            PROXY = obj['proxy_ip'][random_num] + ':' + obj['proxy_port'][random_num]

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
                                """ % (
                                obj['proxy_ip'], obj['proxy_port'], obj['proxy_username'], obj['proxy_password'])
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
                                driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH,
                                                          service_log_path="NULL")
                                totalProxies = len(obj['proxy_ip'])
                else:
                    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH, service_log_path="NULL")
        else:
            driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH, service_log_path="NULL")
        return driver, PROXY, totalProxies
    except Exception as ex:
        print(ex)

def get_proxies():
    # url = "https://www.proxy-list.download/api/v1/get?type=http&anon=elite&country=US"
    # response = requests.get(url)
    # proxies = []
    # resp = response.text
    # resp = resp.split('\r\n')
    # for proxy in resp:
    #     if proxy != '':
    #         proxies.append(proxy)
    url = "https://free-proxy-list.net/"
    soup = bs(requests.get(url).content, "html.parser")
    proxies = []
    for row in soup.find("table", attrs={"id": "proxylisttable"}).find_all("tr")[1:]:
        tds = row.find_all("td")
        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            host = f"{ip}:{port}"
            proxies.append(host)
        except IndexError:
            continue

    return proxies

def get_session(proxies):
    session = requests.Session()
    proxy = random.choice(proxies)
    session.proxies = {"http": proxy, "https": proxy}
    return session, proxy

def autoProxies():
    autoProxy = input("Automatically find free proxies (y/n)?\t")
    if autoProxy == 'y' or autoProxy == 'Y':
        souncloudscrapper(True, False)
    else:
        manualProxy = input("Use custom proxies instead (y/n)?\t")
        if manualProxy == 'y' or manualProxy == 'Y':
            souncloudscrapper(False, True)
        else:
            print("Scrapping Without Proxy")
            souncloudscrapper(False, False)


def song_tiltle_and_rapper_name(name_title,index,index1):
    rapper_name = name_title.split('-')[index]
    rapper_name = replace_all(rapper_name)
    try:
        rapper_name = rapper_name.split('x ')[index]
    except:
        pass
    try:
        rapper_name = rapper_name.split(',')[index]
    except:
        pass
    try:
        rapper_name = rapper_name.split('feat')[index]
    except:
        pass
    try:
        rapper_name = rapper_name.split('Feat')[index]
    except:
        pass
    try:
        rapper_name = rapper_name.split('prod')[index]
    except:
        pass
    try:
        rapper_name = rapper_name.split('(')[index]
    except:
        pass
    try:
        rapper_name = rapper_name.split('and')[index]
    except:
        pass
    try:
        rapper_name = rapper_name.split('&')[index]
    except:
        pass
    try:
        rapper_name = rapper_name.split('+')[index]
    except:
        pass
    try:
        rapper_name = rapper_name.split('[')[index]
    except:
        pass
    try:
        rapper_name = rapper_name.split('|')[index]
    except:
        pass

    try:
        song_title = name_title.split('-')[index1] + name_title.split('-')[2]
    except:
        song_title = name_title.split('-')[index1]
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

    return rapper_name, song_title, song_title_full

def common_email_and_insta(isEmail, isInsta, IG_URL, IG_username, email, dataObj, i, driver):
    username = dataObj['collection'][i]['username']
    permalink_url = dataObj['collection'][i]['permalink_url']
    full_name = dataObj['collection'][i]['full_name']
    country = str(dataObj['collection'][i]['country_code'])
    if email:
        try:
            email = email.group(0)
        except Exception as ex:
            email = email.group(1)
            print(ex)
    location = str(dataObj['collection'][i]['city'])
    name_title = sleep_and_find(
        '//*[@id="content"]/div/div[4]/div[1]/div/div[2]/div/ul/li[1]/div/div/div[2]/div[1]/div/div/div[2]/a/span',
        driver)

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
        rapper_name, song_title, song_title_full = song_tiltle_and_rapper_name(name_title, 0, 1)
        username_list = username.split()
        songtitle_list = song_title.split()
        fullname2_list = full_name2.split()

        counter = 0
        flag_user_name_match = False
        flag_full_name2_match = False
        for sn in songtitle_list:
            for us in username_list:
                if sn == us:
                    counter += 1
                if counter == 2:
                    flag_user_name_match = True
                    break
            if flag_user_name_match:
                break

        lengthOfsongtitle = len(songtitle_list)
        i = 1
        if not flag_user_name_match:
            counter = 0
            for sn in songtitle_list:
                for fn in fullname2_list:
                    if sn == fn:
                        counter += 1
                    if counter == 2:
                        flag_full_name2_match = True
                        break
                if flag_full_name2_match:
                    rapper_name, song_title, song_title_full = song_tiltle_and_rapper_name(
                        name_title, 1, 0)
                    break
                i += 1

        else:
            # print("found in user_name")
            rapper_name, song_title, song_title_full = song_tiltle_and_rapper_name(name_title, 1, 0)

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

        song_title = name_title
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
    if song_title:
        song_title = song_title.encode("ascii", "ignore")
        song_title = song_title.decode()
    if full_name2:
        full_name2 = full_name2.encode("ascii", "ignore")
        full_name2 = full_name2.decode()
    if email:
        email = email.encode("ascii", "ignore")
        email = email.decode()
        if not email.find(":") == -1:
            email = email.split(":")[1]
        if not email.find("/") == -1:
            email = email.split("//")[1]
    if isEmail:
        rapper_list = [username, rapper_name.strip(), full_name2, location, country, permalink_url,
                   email, song_title, song_title_full]
        return rapper_list
    if isInsta:
        rapper_list = [username, rapper_name.strip(), full_name2, location, country, permalink_url,
                       IG_URL, IG_username, song_title, song_title_full]
        return rapper_list

def main_scrapper_function(dataObj, excludes, rapper_data_email, rapper_data_insta, driver, i):
    print(i)
    bio = sleep_and_find('//*[@id="content"]/div/div[4]/div[2]/div/article[1]', driver)
    try:
        show_more = findByXPATH('//*[@id="content"]/div/div[4]/div[2]/div/article[1]/div[1]/div/a', driver)
        show_more.click()
    except:
        pass
    try:
        bio = bio.text
    except:
        bio = ''
        pass

    excluded_word = False
    for exclude in excludes:
        if re.search(exclude, bio, re.IGNORECASE):
            excluded_word = True
            break
    if not excluded_word:
        email = re.search(r'\S+@\S+\.\S+', bio, re.IGNORECASE)
        IG_username, IG_URL = None, None
        if re.search(r'\binstagram\b', bio, re.IGNORECASE):
            web_profiles = sleep_and_find('//*[@id="content"]/div/div[4]/div[2]/div/article[1]/div[2]/ul', driver)
            if web_profiles:
                web_profiles_list = web_profiles.find_elements_by_tag_name('li')
                for i in range(len(web_profiles_list)):
                    href = sleep_and_find('//*[@id="content"]/div/div[4]/div[2]/div/article[1]/div[2]/ul/li[' + str(
                        (i + 1)) + ']/div/a', driver).get_attribute('href')
                    if 'instagram' in href and href is not None:
                        IG_username = href.split(".com%2F")[1].split('&')[0]
                        if not IG_username.find("%2F") == -1:
                            IG_username = IG_username.split("%2F")[0]
                        IG_URL = "https://www.instagram.com/" + IG_username
        if re.search(r'\bIG: @\b', bio, re.IGNORECASE):
            web_profiles = sleep_and_find(
                '//*[@id="content"]/div/div[4]/div[2]/div/article[1]/div[1]/div/div/div/div/p[5]/a[2]', driver)
            if web_profiles:
                IG_username = web_profiles.text
                IG_URL = "https://www.instagram.com/" + IG_username
        if re.search(r'\bI.G: @\b', bio, re.IGNORECASE):
            web_profiles = sleep_and_find(
                '//*[@id="content"]/div/div[4]/div[2]/div/article[1]/div[1]/div/div/div/div/p[5]/a[2]', driver)
            if web_profiles:
                IG_username = web_profiles.text
                IG_URL = "https://www.instagram.com/" + IG_username

        if email is not None:
            rapper_list,  = common_email_and_insta(True, False, None, None, email, dataObj, i, driver)
            rapper_data_email.append(rapper_list)
        if IG_username is not None:
            rapper_list = common_email_and_insta(False, True, IG_URL, IG_username, '', dataObj, i, driver)
            rapper_data_insta.append(rapper_list)
    return rapper_data_email, rapper_data_insta

def proxy_changer(iterate, dataObj, excludes, rapper_data_email, rapper_data_insta, proxies):
    chk_Exception = False
    error = False
    k = 0
    for i in range(iterate):
        s, p = get_session(proxies)
        options.add_argument("proxy-server={}".format(p))
        driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH,
                                  service_log_path="NULL")
        while k < len(dataObj['collection']):
            try:
                permalink = dataObj['collection'][k]['permalink']
                driver.set_page_load_timeout(8)
                driver.get("https://soundcloud.com/" + permalink + "/tracks")
                rapper_data_email, rapper_data_insta = main_scrapper_function(dataObj, excludes, rapper_data_email,rapper_data_insta, driver, k)
                k +=1
            except Exception as ex:
                chk_Exception = True
                proxies = get_proxies()
                break
        if chk_Exception:
            print("Max time is exceeded Switching to other proxy")
            continue
        if i == iterate-1:
            error = True
    return rapper_data_email,rapper_data_insta, error

def souncloudscrapper(use_proxy, use_manual_proxy):
    driver = None
    try:
        print("10000 entries found for scraping")
        entries_start = input("Enter Start Number: ")
        entries = input("Enter Number of entries you want to scrap: ")
        excludes = get_excludes()
        print("Data Scrapping...")
        entry_count = int(entries) / 100
        if entry_count < 1:
            entry_count = 1
        rapper_data_email = []
        rapper_data_instagram = []
        filenameEmail = "SoundCloudRapperDataEmail.csv"
        filenameInstagram = "SoundCloudRapperDataInstagram.csv"
        pCounter = 1
        if not os.path.exists(filenameEmail):
            countEmail = 0
        else:
            countEmail = 1
        if not os.path.exists(filenameEmail):
            countInsta = 0
        else:
            countInsta = 1
        instaFile = open(filenameInstagram, 'a')
        emailFile = open(filenameEmail, 'a')
        portalocker.lock(emailFile, portalocker.LOCK_EX)
        portalocker.lock(instaFile, portalocker.LOCK_EX)
        for n in range(round(entry_count)):
            url = initialurl.replace('<offset>', str((n * 100)+int(entries_start)))
            if use_proxy:
                proxies = get_proxies()
                print(proxies)
                for i in range(25):
                    s, p = get_session(proxies)
                    try:
                        data = s.get(url, timeout=12)
                        dataStr = data.content.decode('utf-8')
                        dataObj = json.loads(dataStr)
                        rapper_data_email, rapper_data_instagram, e = proxy_changer(30, dataObj, excludes, rapper_data_email, rapper_data_instagram, proxies)
                        if e:
                            print("No data found using proxies Try Again.")
                            exit(0)
                    except Exception as e:
                        print("Max time is exceeded Switching to other proxy.")
                        continue
                    if i == 24:
                        print("No data found using auto proxies Try Again.")
                        exit(0)
            elif use_manual_proxy:
                pCounter +=1
                driver, proxy, total_proxies = get_chromedriver()
                proxies = {
                    "http": "http://" + proxy,
                    "https": "http://" + proxy
                }
                try:
                    data = requests.get(url, proxies=proxies)
                except:
                    print("Max time is exceeded Switching to other manual proxy.")
                    continue
                if pCounter == total_proxies:
                    print("No data found using manual proxies Try Again.")
                    exit(0)
                dataStr = data.content.decode('utf-8')
                dataObj = json.loads(dataStr)
                for j in range(len(dataObj['collection'])):
                    permalink = dataObj['collection'][j]['permalink']
                    driver.get("https://soundcloud.com/" + permalink + "/tracks")
                    rapper_data_email, rapper_data_instagram = main_scrapper_function(dataObj, excludes, rapper_data_email, rapper_data_instagram, driver, j)
            else:
                data = requests.get(url)
                dataStr = data.content.decode('utf-8')
                dataObj = json.loads(dataStr)
                driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH,
                                          service_log_path="NULL")
                for j in range(len(dataObj['collection'])):
                    permalink = dataObj['collection'][j]['permalink']
                    try:
                        driver.set_page_load_timeout(10)
                        driver.get("https://soundcloud.com/" + permalink + "/tracks")
                        rapper_data_email, rapper_data_instagram = main_scrapper_function(dataObj, excludes,
                                                                                          rapper_data_email,
                                                                                          rapper_data_instagram, driver,
                                                                                          j)

                    except Exception as ex:
                        print(ex)

            total_results = dataObj['total_results']
            if len(rapper_data_email) > 0:
                countEmail += 1
                portalocker.unlock(filenameEmail)
                rapper_data_df = pd.DataFrame(rapper_data_email)
                rapper_data_df.columns = ['Username', 'FullName', 'FullName2', 'Location', 'Country', 'RapperURL',
                                          'Email', 'SongTitle', 'SongTitleFull', 'InstagramURL', 'InstagramUserName']
                if countEmail == 1:
                    rapper_data_df.to_csv(filenameEmail, mode='a', index=False, header=True)
                else:
                    rapper_data_df.to_csv(filenameEmail, mode='a', index=False, header=False)

                print(str((n + 1) * 100) + " Entries Scrapped Successfully and saved into " + filenameEmail)
                rapper_data_email = []
            else:
                print("No Rapper Found in 100 entries")

            if len(rapper_data_instagram) > 0:
                countEmail += 1
                portalocker.unlock(filenameInstagram)
                rapper_data_df = pd.DataFrame(rapper_data_instagram)
                rapper_data_df.columns = ['Username', 'FullName', 'FullName2', 'Location', 'Country', 'RapperURL',
                                          'InstagramURL', 'InstagramUserName', 'SongTitle', 'SongTitleFull']
                if countInsta == 1:
                    rapper_data_df.to_csv(filenameInstagram, mode='a', index=False, header=True)
                else:
                    rapper_data_df.to_csv(filenameInstagram, mode='a', index=False, header=False)

                print(str((n + 1) * 100) + " Entries Scrapped Successfully and saved into " + filenameInstagram)
                rapper_data_instagram = []
            else:
                print("No Rapper Found in 100 entries")
        if not rapper_data_email or rapper_data_instagram:
            print("No Rapper Found")
        else:
            print('All data Scrapped Successfully and saved in Files')
        k = input("******* press any key to exit ******* \t")
        if k:
            exit(1)
    except Exception as ex:
        print(ex, 'Please first close the file.')
        k = input("******* press any key to exit *******")
        if driver is not None:
            driver.quit()

def main():
    autoProxies()

if __name__ == "__main__":
    main()
