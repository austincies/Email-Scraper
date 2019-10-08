import bs4
import re
import requests
import queue
import urllib
import sys


class mailSpider:

    def __init__(self, scope, maxEmail):
        self.visited = set()
        self.to_visit = queue.Queue()
        scope = scope.strip("http://")
        scope = urllib.parse.urlparse("//" + scope)[1] 
        self.to_visit.put(scope)
        self.emails = set()
        self.emailCount = 0
        self.maxEmails = maxEmail
        self.scope = scope

    def linkValid(self, anchor):
        if len(anchor) == 0:
            return False
        elif anchor[0] == "w" or anchor[0] == "h" or anchor[0] == "/":
            return True
        else:
            return False

    def inScope(self, url):
        if url == self.scope:
            return True
        try:
            url = url.split('.')
            s = self.scope.split('.')
            if url[len(url) - 1] == s[len(s) - 1] and url[len(url) - 2] == s[len(s) - 2]:
                return True
            else:
                return False
        except:
            return False

    def scrape(self, url):
        self.visited.add(url)
        try:
            u = urllib.parse.urlparse("https://" + url)
            response = requests.get("https://" + url)

            newEmails = set(re.findall(
                r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
            for email in newEmails:
                if self.emailCount >= self.maxEmails:
                    return
                if email not in self.emails:
                    self.emailCount = self.emailCount + 1
                    self.emails.add(email)

            soup = bs4.BeautifulSoup(response.text, 'html.parser')
            for newLink in soup.find_all('a', href=True):
                try:
                    anchor = newLink['href']
                    if self.linkValid(anchor) == False:
                        next
                    else:
                        if anchor[0] == "/":
                            anchor = u[1] + anchor
                        aUrl = urllib.parse.urlparse(anchor)
                        if aUrl[1] == '':
                            aUrl = urllib.parse.urlparse("//" + anchor)
                        if self.inScope(aUrl[1]) and (aUrl[1] + aUrl[2]) not in self.visited:
                            self.to_visit.put(aUrl[1] + aUrl[2])
                except:
                    next
        except:
            pass


    def saveEmails(self):
        f = open("emails.txt", "a")
        for email in self.emails:
            f.write(email + "\n")

    def crawl(self):
        while True:
            if self.emailCount >= self.maxEmails:
                break
            elif self.to_visit.empty():
                break
            else:
                url = self.to_visit.get()
                self.scrape(url)
        self.saveEmails()


def main():
    if len(sys.argv) != 3:
        print("Usage: emailScraper.py [url], [emailCount]")
    url = sys.argv[1]
    maxEmail = sys.argv[2]
    spider = mailSpider(url, int(maxEmail))
    spider.crawl()


main()
