import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys
import re

imgNo = 0

def writeImg(img_src_paths , domain):
    global imgNo
    for img_url in img_src_paths:
        print(img_url)
        try:
            re = requests.get(img_url)
        except:
            continue
        imgNo  = imgNo+ 1
        filename = str(imgNo) + "." + img_url.split('.')[-1]
        f = open(domain+'/'+filename, 'wb')
        f.write(re.content)
        f.close()


def getImgHtml(url , soup , domain):
    img_tags = soup.find_all('img')
    img_src_paths = set()
    for i in img_tags:
        src = i.get('src')
        if not src:
            continue
        if src[:7] == 'http://' or src[:8] == 'https://':
            img_src_paths.add(src)
        else:
            img_src_paths.add(urljoin(url, src))
    print("saving img from html:")
    writeImg(img_src_paths , domain)


def getImgStyle(soup , htmlPath , domain):
    style = soup.findAll("style");
    img_src_path = set()
    for s in style:
        for path in re.findall(r'url\(([^)]+)\)' , s.string):
            if(path[:1] == "\'"):
                img_src_path.add(urljoin(htmlPath , path.split("\'")[1]))
            elif(path[:1] == "\""):
                img_src_path.add(urljoin(htmlPath , path.split("\"")[1]))
            else:
                img_src_path.add(urljoin(htmlPath , path))
    print("images from style")
    writeImg(img_src_path , domain)


def getImgCss(htmlUrl , soup , domain):
    css_paths = set()
    for link in soup.findAll("link" , {"rel" : "stylesheet"}):
        css_paths.add(urljoin(htmlUrl , link.attrs["href"]))
    img_src_path = set()
    for link in css_paths:
        req = requests.get(link)
        for path in re.findall(r'url\(([^)]+)\)' , req.text):
            if(path[:1] == "\'"):
                img_src_path.add(urljoin(link , path.split("\'")[1]))
            elif(path[:1] == "\""):
                img_src_path.add(urljoin(link , path.split("\"")[1]))
            else:
                img_src_path.add(urljoin(link , path))
    print("images from css files")
    writeImg(img_src_path , domain)
    return


def download(url):
    domain = url.split('//')[-1].split('/')[0]
    os.makedirs(domain)
    response = requests.get(url)
    if response.status_code != 200:
        return
    soup = BeautifulSoup(response.text , "lxml")
    getImgHtml(url , soup , domain)
    getImgStyle(soup , url , domain)
    getImgCss(url , soup , domain)
    return

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Enter a website url to fetch images")
    else:
        download(sys.argv[1])
