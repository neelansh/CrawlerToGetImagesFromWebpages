import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys
import re

def getAbsPath(baseUrl , imgPath):
    return urljoin(baseUrl , imgPath)

def getImgfromSyle(soup , filepath):
    style = soup.findAll("style");
    result = ""
    for s in style:
        result = result + s.string
    resu = re.findall(r'url\(([^)]+)\)' , result)
    resu = resu + re.findall(r'url\("([^)]+)"\)' , result)
    resu = resu + re.findall(r'url\(\'([^)]+)\'\)' , result)
    i=0
    print(resu)
    returnitem = []
    for res in resu:
        returnitem[i] = getAbsPath(filepath , res)
        i += 1
    return returnitem

def getimgCss(baseUrl , cssUrl):
    req = requests.get(cssUrl)
    result = re.findall(r'url\("([^)]+)"\)' , req.text)
    result = result + re.findall(r'url\(\'([^)]+)\'\)' , req.text)
    result = result + re.findall(r'url\(([^)]+)\)' , req.text)
    i=0
    print(result)
    for res in result:
        result[i] = getAbsPath(cssUrl , res)
        i += 1
    return result


def download(url):
    domain = url.split('//')[-1].split('/')[0]
    os.makedirs(domain)
    response = requests.get(url)
    if response.status_code != 200:
        return
    soup = BeautifulSoup(response.text , "lxml")
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

    css_links = soup.findAll("link" , {"rel":"stylesheet"})
    i = 0
    for link in css_links:
        css_links[i] = link.attrs["href"]
        i+=1

    print(css_links)
    for link in css_links:
        result = getimgCss(url , urljoin(url , str(link)))
        for i in result:
            img_src_paths.add(i)

    result = getImgfromSyle(soup , url)
    for i in result:
        img_src_paths.add(i)

    i = 0
    for img_url in img_src_paths:
        print(img_url)
        try:
            re = requests.get(img_url)
        except:
            continue
        i  = i + 1
        filename = str(i) + "." + img_url.split('.')[-1]
        f = open(domain+'/'+filename, 'wb')
        f.write(re.content)
        f.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Enter a website url to fetch images")
    else:
        download(sys.argv[1])
