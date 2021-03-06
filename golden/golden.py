import requests
from bs4 import BeautifulSoup
# from proxies import proxies
import sys
import nltk
from nltk import sent_tokenize

def extractPageContent(url):
    try:
        page = requests.get(url)
    except:
        print("Error while trying to get page")
        # sys.exit()
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup

def getFirstSearchResult(user_query):
    # query = input("What is your query ?\n")
    base_url = 'https://golden.com'
    base_search_url = 'https://golden.com/search/'
    search_url = base_search_url + user_query
    soup = extractPageContent(search_url)
    links_list = []
    for link in soup.find_all('a'):
        links_list.append(link.get('href'))
    first_result = links_list[3]
    first_result_link = base_url + first_result
    return first_result_link

def getQueryUrl():
    base_url = 'https://golden.com/wiki/'
    query = getSearchResult()
    url = base_url + query
    return url

def download(user_query):
    search_url = getFirstSearchResult(user_query)
    try:
        page = requests.get(search_url)
    except:
        return "Error while trying to get page"
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup

def title(soup):
    title = soup.find("h1", {"class": "TopicDetail__header__headline--inner"}).get_text()
    return title

def summary(soup):
    summary = []
    summary = soup.find("div", {"class": "TopicDetail__abstract"}).get_text()
    return summary

def content(soup, sentences=1):
    content_abstract = soup.find("div", {"class": "TopicDetail__body"})
    first_section = content_abstract.find("div", {"class": "TopicDetail__overview__block"})
    text_content = first_section.find("div", {"class": "Editor--article"})
    if not text_content:
        print("No content to display.")
        return
    if len(text_content.findAll("p", {"class": "Editor__text"})) == 0:
        return "No content to display"
    elif len(text_content.findAll("p", {"class": "Editor__text"})) == 1:
        try:
            content = text_content.findAll("p", {"class": "Editor__text"}).get_text()
        except:
            return "No content to display"
        content_sent = sent_tokenize(content)
        description = " ".join(content_sent[0:sentences])
    else:
        i=0
        content = []
        while i < len(text_content.findAll("p", {"class": "Editor__text"})):
            content.append(text_content.findAll("p", {"class": "Editor__text"})[i].get_text())
            i+=1
        description = " ".join(content[0:sentences])
    if description:
        return description

def timeline(soup, events=0):
    timeline_block = soup.findAll("div", {"class": "EntityTimeline"})
    events_list = []
    i=0
    while i <= events:
        try:
            event = {}
            event["date"] = timeline_block[0].findAll("div", {"class": "TimelineEvent__date"})[i].get_text()
            event["subtitle"] = timeline_block[0].findAll("h3")[i].get_text()
            event["content"] = timeline_block[0].findAll("p")[i].get_text()
            events_list.append(event)
        except:
            print(i, "events loaded.")
            break
        i+=1
    return events_list

def people(soup, position=''):
    table = soup.find('div', {"class": "table"})
    rows = table.findAll('div', {"class": "table-row__wrapper"})
    rows_list = []
    for row in rows:
        name = row.findAll("div", {"class": "table-cell"})[0].get_text()
        role = row.findAll("div", {"class": "table-cell"})[1].get_text()
        golden_related = row.findAll("div", {"class": "table-cell"})[2].get_text()
        result = {}
        result["name"] = name
        result["role"] = role
        result["golden_related"] = golden_related
        rows_list.append(result)
    # remove first header row
    rows_list = rows_list[1:]
    final_list = []
    if position:
        for row in rows_list:
            if position in row["role"]:
                final_list.append(row)
    if final_list:
        return final_list
    elif rows_list:
        return rows_list
    else:
        return "No people to display for this query."

