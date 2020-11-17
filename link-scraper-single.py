from bs4 import BeautifulSoup
from urllib.request import Request, urlopen, urljoin, HTTPError, URLError
from http.client import InvalidURL
import re

website = input("Website: >> ") # without http/https part
filename = "{}-links.txt".format(website.split("://")[1].split("/")[0])

links = []
completed = []

def findlinks(page):
    all = []
    req = Request(page)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36')
    html_page = urlopen(req)
    soup = BeautifulSoup(html_page, "lxml")

    for link in soup.findAll('a'):
        li = link.get('href')
        if "http://" not in str(li) and "https://" not in str(li):
            if len(str(li)) > 1:
                final = urljoin(page, li)
                if str(final)[-1:] == "/":
                    final = final[:-1]
                all.append(final)
    return all

links = findlinks(website)
completed.append(website)

while True:
    c_error = ""
    newlinks = []
    try:
        for i in links:
            if not i in completed:
                c_error = str(i)
                newlinks += findlinks(i)
                print("Indexed: " + str(i))
                links += newlinks
                links = list(set(links))
                completed.append(i)
                with open(filename, 'w') as linkfile:
                    for i in links:
                        linkfile.write(i + "\n")
    except KeyboardInterrupt:
        print("Links Identified: " + str(len(completed)))
        print("Writing current data to file")
        open(filename, 'w').close()
        with open(filename, 'w') as linkfile:
            for i in links:
                linkfile.write(i + "\n")
        exit()
    except (HTTPError, URLError, InvalidURL):
        print("Error: " + c_error)
        completed.append(c_error)
        pass