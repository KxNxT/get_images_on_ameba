from pprint import pprint
from urllib3 import PoolManager
from bs4 import BeautifulSoup
import csv
import datetime
import glob
import os
import urllib3

urllib3.disable_warnings()

outputDir = "./html/"
configDir = "./csv/"
cs = ['caw=800',
      'frm_src=favoritemail',
      'utm_medium=ameba',
      'utm_content=official__mm-12ki',
      'utm_campaign=gamp_officialRecommend',
      'utm_source=gamp',
      'utm_campaign=gamp_reactions',
      'device_id=055aaf9edd7a451ab72d73f259c2b91c',
      'frm_id=v.jpameblo',
      '&']

class AmebloAccessError(Exception):
    "Amebloへ繋げる時に発生するエラー"

class Page():
    def __init__(self, url):
        try:
            self.url = 'https://ameblo.jp' + url
            POOL_MNG = PoolManager()
            html = POOL_MNG.request("GET", self.url)
            self.soup = BeautifulSoup(html.data, "html.parser")
        except Exception:
            raise AmebloAccessError(Exception)

    def getNextUrl(self):
        url = self.soup.find(
            "a", attrs={'data-uranus-component': "entryPagingPrev"}).get('href')
        return self.remove_param(url)

    def getImages(self):
        body = self.soup.find(id="entryBody")
        images = []
        for img in body.find_all("img"):
            if(img is None or img.get("src") is None):continue
            images.append(self.remove_param(img.get("src")))
        return images

    def remove_param(self, url):
        if(url is None ):
            return None
        for c in cs:
            url = url.replace(c, '')
        return url



class Blog():
    def __init__(self,name,url):
        self.name = name
        self.url = url


class Config():
    def __init__(self, filename):
        self.filename = filename
        self.blogs = []

    def getBlogs(self):
        csv_file = open(self.filename, "r", newline="")
        rows = csv.reader(csv_file, delimiter=",")
        b = []

        for row in rows:
            b = Blog(row[0], row[1])
            self.blogs.append(b)
        return self.blogs

    def add(self, blog):
        self.blogs.append(blog)

    def save(self):
        with open(self.filename, "w", newline="") as f:
            for blog in self.blogs:
                w = csv.writer(f, delimiter=",")
                w.writerow([blog.name, blog.url])


class Html():
    def __init__(self, filename):
        self.urls = []
        self.filename = filename

    def addImageUrl(self, urls):
        self.urls.extend(urls)

    def makeHtml(self):
        s = '<html><body>'
        for url in self.urls:
            s = s + '<img src="' + url + '">'
        s = s + '</body></html>'
        with open(self.filename, mode='w') as f:
            f.write(s)


csvs = []
for r in glob.glob(configDir + '*.csv'):
    csvs.append(os.path.basename(r))

config = Config(configDir + max(csvs))
blogs = config.getBlogs()

todaydetail = datetime.datetime.today()
nextConfig = Config(
    configDir + todaydetail.strftime("%Y-%m-%d_%Hh%Mm%Ss") + '.csv')

html = Html(outputDir + todaydetail.strftime("%Y-%m-%d_%Hh%Mm%Ss") + '.html')

for blog in blogs:
    try:
        p = Page(blog.url)
    except Exception:
        print("Error Ameba access...skip L107 :" + blog.name)
        print(Exception)
        newBlog = Blog(blog.name, lastUrl)
        nextConfig.add(newBlog)
        continue

    print("START [" + blog.name + "] first url=>" + blog.url)
    lastUrl = blog.url
    nextUrl = p.getNextUrl()
    newBlog = Blog(blog.name, lastUrl)
    while (nextUrl):
        print("Getting... BLOG NAME : " + blog.name + " => " + nextUrl)
        p = None
        try:
            p = Page(nextUrl)
        except Exception:
            print("Error Ameba access...skip L122:" + blog.name)
            print(Exception)
            newBlog = Blog(blog.name, lastUrl)
            break
        images = p.getImages()
        html.addImageUrl(images)

        lastUrl = nextUrl
        nextUrl = p.getNextUrl()
        newBlog = Blog(blog.name, lastUrl)

    nextConfig.add(newBlog)

nextConfig.save()
html.makeHtml()
