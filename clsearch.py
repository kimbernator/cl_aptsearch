import requests
import argparse
import time
from time import gmtime, strftime
import db
import notify
import AptCheck
from bs4 import BeautifulSoup as bs4

# Instantiate DB connection class
cldbconn = db.CLDB()
# Instantiate slack connection
slack_key = ""
slacker = notify.NOTIF(slack_key)
# Prepare other variables
url_base = 'http://<city>.craigslist.org/search/apa'
params = dict(search_distance=2, postal=<zip>, min_price=700, max_price=1250)
firstrun = True

def reset():
    db.reset()
    print('Database reset.')
    exit

# parser = argparse.ArgumentParser(description='Search for apartments.')
# parser.add_argument('--reset', action=reset)
# args = parser.parse_args()

while True:
    rsp = bs4(requests.get(url_base, params=params).text, 'html.parser')
    apts = rsp.find_all('li', attrs={'class': 'result-row'})

    for apt in apts:
        aptlink = apt.find('a', attrs={'class': 'result-title hdrlnk'})['href']
        if cldbconn.discover(int(apt['data-pid'])):
            if firstrun == False:
                break
            else:
                continue
        else:
            data_form = {
                'id_submission': int(apt['data-pid']),
                'title': apt.find('a', attrs={'class': 'result-title hdrlnk'}).string,
                'link': aptlink
            }
            cldbconn.insert(data_form)

        # Get apt link and instantiate the APARTMENT class with the page's html
        aptlink = apt.find('a', attrs={'class': 'result-title hdrlnk'})['href']
        aptpage = bs4(requests.get(aptlink).text, 'html.parser')
        this_apt = AptCheck.APARTMENT(aptpage)

        assessment = this_apt.score()
        if assessment == 'R':
            print("skipping QH")
            continue
        elif assessment['Score'] >= 5:
            slacker.post(assessment, aptlink)

        firstrun = False
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    time.sleep(30)
