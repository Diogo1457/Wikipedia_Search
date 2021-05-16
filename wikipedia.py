import requests as r
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("query", help="What you want to search")
args = parser.parse_args()

query = args.query

url = "https://en.wikipedia.org/wiki/"

def filterHTMLTags(content_parg):
    content = ""
    cont = 0
    for c in content_parg:
        if cont >= len(content_parg): # Filtrar mais
            break
        close_tag = content_parg.find(">", cont) + 1
        open_tag = content_parg.find("<", close_tag)
        content += content_parg[close_tag:open_tag:1]
        cont = close_tag + 2
    return content


def filterAnds(content):
    _and = 0
    for c in content:
        if _and >= len(content):
            break
        start_and = content.find("&", _and)
        end_and = content.find(";", start_and) + 1
        content = content.replace(content[start_and:end_and:1], "")
        _and = end_and + 2
    return content


def filterContent(content_old):
    start_text = content_old.find("mw-parser-output")
    start_parg = content_old.find("<p>", start_text)
    end_parg = content_old.find("</p>", start_parg)
    content_parg = content_old[start_parg:end_parg:1]
    content = filterHTMLTags(content_parg)
    content = content[0:content.rfind(".")+1:1]
    content = filterAnds(content)
    return content.strip()


def getLinkName(links):
    links_dict = {}
    for l in links:
        title = l.replace("/wiki/", "").replace("_", " ").replace("%27", "'")
        links_dict[title] = l
    return links_dict


def isValidLink(link, query):
    is_valid = True
    if not query in link:
        is_valid = False
    if link[0:6:1] != "/wiki/":
        is_valid = False
    if "Special:" in link or "/wiki/" + query == link or "Talk:" in link:
        is_valid = False
    return is_valid


def beautifySearch(query):
    query = query.strip()
    search_list = query.split(" ")
    query = ""
    for c in search_list:
        query += (c.capitalize() + " ")
    query = query.strip().replace(" ", "_")
    return query


def filterContentList(content_old, query):
    start_text = content_old.find("mw-parser-output")
    content_list = []
    for c in content_old:
        start_link = content_old.find('<a href="', start_text) + 9
        end_link = content_old.find('"', start_link)
        content = filterHTMLTags(content_old[start_link:end_link:1])
        content = content_old[start_link:end_link:1] # Filtrar mais
        if content in content_list:
            break
        if isValidLink(content, query):
            content_list.append(content)
        start_text = end_link + 2
    links = getLinkName(content_list)
    return links


def line(n, s="-"):
    print(n * s)


def header(msg):
    line(50)
    print(f"{msg:^50}")
    line(50)


def menu(lista):
    c = 1
    for l in lista:
        if c < 10:
            print(f"[{'0' + str(c)}] - {l}")
        else:
            print(f"[{c}] - {l}")
        c += 1
    line(50)


def readStr(msg):
    while True:
        try:
            n = str(input(msg))
            if str(n) == "exit":
                return None
                break
            else:
                n = int(n)
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
        except:
            print("Must be an integer")
        else:
            return n
            break



def changeDictToList(content_list):
    content = []
    for c in content_list:
        content.append(c)
    return content


def getInput(content_list, query):
    links = content_list
    while True:
        option = readStr(f"What you want to know about {query}? ")
        if option:
            if option >= 1 and option <= len(links):
                link = links[option - 1]
                return link
                break
            else:
                print("Invalid Option")
        else:
            return None
            break


def cleanRepeatedContent(content):
    end_phrase = content.find(".") + 1
    first_phrase = content[0:end_phrase:1]
    content = content[0:content.find(first_phrase, end_phrase):1]
    return content


def search(query, language="en"):
    header(f"Looking for {query}")
    query = beautifySearch(query)
    req = r.get(url + query)
    content_no_filters = req.text
    if "most commonly refers to:" not in content_no_filters and "may refer to:" not in content_no_filters:
        content = filterContent(content_no_filters)
        actual_url = req.url
        word = actual_url[actual_url.find("/wiki/") + 6::1].replace(")", " ").replace("(", "").replace("_", " ").strip()
        content = cleanRepeatedContent(content)
        if len(content) != 0:
            return content, word
        else:
            return "Anything found", word
        line(50)
    else:
        content_dict = filterContentList(content_no_filters, query)
        content_keys = changeDictToList(content_dict.keys())
        content_values = changeDictToList(content_dict.values())
        if len(content_values) != 0:
            menu(content_keys)
            link = getInput(content_values, query)
            if link:
                return search(link.replace("/wiki/", "").replace(",", "").replace(":", ""))
            else:
                return None,
        else:
            return "Anything found",

query = query.replace("_", " ")
resposta = search(query)[0]
if resposta:
    print(resposta)

