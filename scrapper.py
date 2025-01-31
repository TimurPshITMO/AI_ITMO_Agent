from bs4 import BeautifulSoup
import requests
import re

def findURLs(s):
    return re.findall(r"(?P<url>https?://[^\s]+)", s)

def findNumber(s):
    if 'None' in s[:min(len(s),6)]:
        return None
    match = re.search(r'\d+', s)
    if match:
        return int(match.group())
    else:
        return None

def getWebInfo(url, log):
    
    result = requests.get(url)
    content = result.text
    soup = BeautifulSoup(content, 'lxml')
    
    links = []
    for i in soup.find_all('a', href=True):
        label = i.get_text(strip = True)
        if len(label)>0:
            if i['href'].find('http')<0:
                links.append((label, url+i['href']))
            else:
                links.append((label, i['href']))
    
    text = soup.find('body').get_text(strip=True, separator='\n')

    log(f"URL scrabbed: {url}")

    return {'text' : text, 'links' : links}