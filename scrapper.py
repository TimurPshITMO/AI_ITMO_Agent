from bs4 import BeautifulSoup
import requests
import re

def findURLs(s):

    """
    Поиск всех ссылок в тексте
    """

    return re.findall(r"(?P<url>https?://[^\s\[\]\(\)]+)", s)

def findNumber(s):

    """
    Определение номера ответа (первое числовое значение в ответе четвертого агента или None)
    """

    if 'None' in s[:min(len(s),10)]:
        return None
    match = re.search(r'\d+', s)
    if match:
        try:
            return int(match.group())
        except ValueError as e:
            return None
    else:
        return None


def getWebInfo(url, log):
    
    """
    Тул для скрэмблинга... скрэппинга... короче для поиска текста по ссылкам

    Читает страничку по адресу, возвращает чистый текст с нее и пары (название, адрес) ссылок на ней
    """

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