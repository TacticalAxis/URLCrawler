import mysql.connector
from bs4 import BeautifulSoup, Comment
from urllib.request import Request, urlopen, urljoin, HTTPError, URLError
from mysql.connector.errors import DataError, OperationalError
from http.client import InvalidURL
import time
import re
import os
from auth import *

mydb = mysql.connector.connect(
  host = getHost(),
  user = getUser(),
  password = getPass(),
  database = getDatabase()
)

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'header', 'noscript', 'html', 'meta', 'input',  'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

sql = mydb.cursor()

for filename in os.listdir("Output"):
    with open('Output\\{}'.format(filename),'r') as f:
        for url in f:
            if not str(url)[-4:] == ".rss":
                try:
                    req = Request(url)
                    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36')
                    html_page = urlopen(req)
                    soup = BeautifulSoup(html_page, 'html.parser')
                    texts = soup.findAll(text=True)
                    visible_texts = filter(tag_visible, texts)  
                    output = " ".join(t.strip() for t in visible_texts)
                    title = soup.find('title')
                    title = title.string
                    title = title.replace("'","''").replace("\"","\"\"")
                    url = url.replace("'","''").replace("\"","\"\"")
                    output = output.replace("'","''").replace("\"","\"\"")
                    output = ''.join(output.split("\n"))
                    output = re.sub(' +', ' ', output)
                    sql.execute("SELECT * FROM `link_content` WHERE `url`='{}';".format(url))
                    exists = sql.fetchall()
                    if len(exists) > 0:
                        print("URL from \"{}\" Exists, Updating!".format(url.split("://")[1].split("/")[0]))
                        print(str(url).strip())
                        sql.execute("UPDATE link_content SET `updated`='{}',`title`='{}',`content`='{}' WHERE url='{}';".format(time.strftime('%Y-%m-%d %H:%M:%S'), title, output, url))
                    else:
                        print("URL from \"{}\" Does not Exist, Creating Link".format(url.split("://")[1].split("/")[0]))
                        print(str(url).strip())
                        sql.execute("INSERT INTO link_content(`updated`,`title`, `url`,`content`) VALUES('{}','{}','{}','{}');".format(time.strftime('%Y-%m-%d %H:%M:%S'), title, url, output))
                except KeyboardInterrupt:
                    print("Stopping Operation")
                    exit()
                except (HTTPError, URLError, DataError, InvalidURL):
                    print("Error with " + (str(url).strip()))
                    pass
                except AttributeError:
                    print("Severe error w/ {}".format(url))
                    pass