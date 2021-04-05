import os
import random
import re
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

def get_proxies():
    url = "https://free-proxy-list.net/"
    # get the HTTP response and construct soup object
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
    # choose one random proxy
    proxy = random.choice(proxies)
    session.proxies = {"http": proxy, "https": proxy}
    return session, proxy

def autoProxies():
    autoProxy = input("Automatically find free proxies (y/n)?")
    if autoProxy == 'y' or autoProxy == 'Y':
        souncloudscrapper(True)
    else:
        souncloudscrapper(False)

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

def main_scrapper_function(dataObj, excludes, rapper_data, driver, i):
    # for i in range(len(dataObj['collection'])):
    print(i)
    permalink = dataObj['collection'][i]['permalink']
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

        if email is not None or IG_username is not None:
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
            # cn = ''
            # if country:
            #     cn = country if country else ''
            # location = str(dataObj['collection'][i]['city'])
            # location_sl = ''
            # if not location.find("/") == -1:
            #     location_sl = sleep_and_find('//*[@id="content"]/div/div[2]/div/div[1]/div/div[2]/h4[2]')
            #     location_sl = location_sl.text
            #     try:
            #         location_sl = str(location_sl).split(", ")[1]
            #     except:
            #         location_sl = ''
            # if location_sl == '':
            #     location = location_sl +  " " + cn

            # else:
            #     location = location + " " + cn
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

            rapper_list = [username, rapper_name.strip(), full_name2, location, country, permalink_url,
                           email, song_title, song_title_full, IG_URL, IG_username]
            rapper_data.append(rapper_list)
    return rapper_data

def proxy_changer(iterate, dataObj, excludes, rapper_data, proxies):
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
                rapper_data = main_scrapper_function(dataObj, excludes, rapper_data, driver, k)
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
    return rapper_data, error

def souncloudscrapper(use_proxy):
    try:
        print("10000 entries found for scraping")
        entries_start = input("Enter Start Number: ")
        entries = input("Enter Number of entries you want to scrap: ")
        excludes = ['DJ', 'repost', 'management', 'group', 'agency', 'singer', 'beat', 'producer', 'prod by']
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
        with open(filename, 'a') as file:
            portalocker.lock(file, portalocker.LOCK_EX)
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
                            rapper_data, e = proxy_changer(30,dataObj,excludes,rapper_data, proxies)
                            if e:
                                print("No data found using proxies Try Again.")
                                exit(0)
                        except Exception as e:
                            print("Max time is exceede Switching to other proxy")
                            continue
                        if i == 24:
                            print("No data found using proxies Try Again.")
                            exit(0)

                else:
                    data = requests.get(url)
                    dataStr = data.content.decode('utf-8')
                    dataObj = json.loads(dataStr)
                    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH,
                                              service_log_path="NULL")
                    for j in range(len(dataObj['collection'])):
                        permalink = dataObj['collection'][j]['permalink']
                        driver.get("https://soundcloud.com/" + permalink + "/tracks")
                        rapper_data = main_scrapper_function(dataObj, excludes, rapper_data, driver, j)

                total_results = dataObj['total_results']
                if len(rapper_data) > 0:
                    count += 1
                    portalocker.unlock(file)
                    rapper_data_df = pd.DataFrame(rapper_data)
                    rapper_data_df.columns = ['Username', 'FullName', 'FullName2', 'Location', 'Country', 'RapperURL',
                                              'Email', 'SongTitle', 'SongTitleFull', 'InstagramURL', 'InstagramUserName']
                    if count == 1:
                        rapper_data_df.to_csv(filename, mode='a', index=False, header=True)
                    else:
                        rapper_data_df.to_csv(filename, mode='a', index=False, header=False)

                    print(str((n + 1) * 100) + " Entries Scrapped Successfully and saved into " + filename)
                    rapper_data = []
                else:
                    print("No Rapper Found in 100 entries")

        print('All data Scrapped Successfully and saved in File ' + filename)
        k = input("******* press any key to exit *******")
    except Exception as ex:
        print(ex, 'Please first close the file.')
        k = input("******* press any key to exit *******")
    driver.quit()

def main():
    autoProxies()

if __name__ == "__main__":
    main()
