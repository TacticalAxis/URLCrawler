from bs4 import BeautifulSoup
from queue import Queue, Empty
from threading import Thread
from urllib.request import Request, urlopen, urljoin, HTTPError, URLError
from http.client import InvalidURL
from time import sleep
from pathlib import Path

website = input("Website: >> ") # without http/https part
filename = "{}-links.txt".format(website.split("/")[0])


visited = set()
queue = Queue()
    
def getParser(host, root, charset):
    def parse():
        try:
            while True:
                page = queue.get_nowait()
                html_page = None
                try:
                    req = Request(page)
                    if page[-4:] == ".rss":
                        raise InvalidURL
                    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36')
                    html_page = urlopen(req)
                except (UnicodeEncodeError, InvalidURL, HTTPError):
                    continue
                soup = BeautifulSoup(html_page, "lxml")
                for link in soup.findAll('a'):
                    try:
                        href = link['href']
                    except KeyError:
                        continue
                    if not href.startswith('https://'):
                        href = 'https://%s%s' % (host, href)
                    if not href.startswith('https://%s%s' % (host, root)):
                        continue
                    if href not in visited:
                        visited.add(href)
                        queue.put(href)
                        print(href)
        except Empty:
            pass
    return parse

def filePrinter():
    def save():
        sleep(3)
        print("Printing data now!")
        with open(filename, 'w') as f:
            for i in list(visited):
                f.write(i + "\n")
    return save

if __name__ == '__main__':
    host, root, charset = website,"/",'utf-8'
    parser = getParser(host, root, charset)
    savefile = filePrinter()
    queue.put('https://%s%s' % (host, root))
    workers = []
    for i in range(5):
        worker = Thread(target=parser)
        worker.start()
        workers.append(worker)
    saver = Thread(target=savefile)
    saver.start()
    for worker in workers:
        worker.join()
    saver.join()