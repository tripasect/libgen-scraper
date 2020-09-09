import os
import requests
from bs4 import BeautifulSoup as BS
import wget


def cls():
    """Wipes the screen altogether. Works on Linux BASH and Windows Command Line.
    Should also work on Mac OS, not sure."""
    os.system('cls' if os.name == 'nt' else 'clear')


def search(query):
    search_base = "http://libgen.rs/search.php?req={}&lg_topic=libgen&open=0&view=simple&res=25&phrase=1&column=def"
    search_page = search_base.format(query.replace(' ', '+'))
    page = requests.get(search_page)
    raw_html = page.text
    soup = BS(raw_html, features='html5lib')
    results = []
    table_body = soup.find_all(valign="top")[1:]
    for row in table_body:
        item = {}
        data = row.findAll(width="500")
        for record in data:
            href = record.find(name='a').get('href')
            item['url'] = 'http://libgen.rs/' + href
        tds = row.find_all('td')
        tds = [td.text for td in tds]
        item['author'] = tds[1]
        item['title'] = tds[2]
        item['publisher'] = tds[3]
        try:
            item['year'] = int(tds[4])
        except ValueError:
            item['year'] = tds[4]
        item['pages'] = tds[5]
        item['langauge'] = tds[6]
        try:
            if 'mb' in tds[7].lower():
                item['size'] = float(tds[7].split()[0])
            elif 'kb' in tds[7].lower():
                item['size'] = float(tds[7].split()[0]) / 1000
        except ValueError:
            item['size'] = tds[7]
        item['extension'] = tds[8]
        results.append(item)
    return results


def decide(results):
    if results != []:
        epubs_with_year = []
        epubs_without_year = []
        for result in results:
            if result['extension'] == 'epub':
                if type(result['year']) == int:
                    epubs_with_year.append(result)
                else:
                    epubs_without_year.append(result)
            else:
                pass
        epubs = sorted(epubs_without_year,
                       key=lambda i: i['year'], reverse=True)
        if epubs_with_year != []:
            return epubs_with_year[0]
        elif epubs_without_year != []:
            return epubs[0]
        else:
            pdfs_with_year = []
            pdfs_without_year = []
            for result in results:
                if result['extension'] == 'pdf':
                    if type(result['year']) == int:
                        pdfs_with_year.append(result)
                    else:
                        pdfs_without_year.append(result)
                else:
                    pass
            pdfs_without_year = sorted(
                pdfs_with_year, key=lambda i: i['year'], reverse=True)
            if pdfs_with_year != []:
                return pdfs_with_year[0]
            elif pdfs_without_year != []:
                return pdfs_without_year[0]
            else:
                return None
    else:
        return None


def mirrors(decision):
    page = requests.get(decision['url'])
    raw_html = page.text
    soup = BS(raw_html, features='html5lib')
    mirrors_messed = soup.find_all(valign="top")[-4]
    mirrors_better = mirrors_messed.find_all(name='a')
    mirrors = []
    for mirror in mirrors_better[:4]:
        item = {}
        item['name'] = mirror.get('title')
        item['url'] = mirror.get('href')
        mirrors.append(item)
    return mirrors


def mirror_to_url(mirrors, mirror):
    if mirror == 'gen-lib-rus-ec':
        redirect = mirrors[0]['url']
        page = requests.get(redirect)
        raw_html = page.text
        soup = BS(raw_html, features='html5lib')
        url = soup.h2.find(name='a').get('href')
        return url
    if mirror == 'libgen-lc':
        redirect = mirrors[1]['url']
        page = requests.get(redirect)
        raw_html = page.text
        soup = BS(raw_html, features='html5lib')
        url = soup.body.table.tbody.tr.find_all(
            'td')[1].find(name='a').get('href')
        return url
    else:
        pass


def download(url, save_name):
    wget.download(url, out=save_name)


seperator = 126 * '━'


def do_it_all(book, mirror):
    try:
        print("DOWNLOADING...")
        print(f"Title: \"{book['title']}\"\nAuthor: \"{book['author']}\"")
        query = book['title'] + ' ' + book['author']
        entries = search(query)
        if entries != []:
            decision = decide(entries)
            mirrs = mirrors(decision)
            download_url = mirror_to_url(mirrs, mirror)
            print("Mirror:", mirror)
            print("URL:", download_url, sep='\n')
            save_name = book['title'] + ' - ' + \
                book['author'] + '.' + decision['extension']
            download(download_url, save_name)
            book['downloaded'] = True
            print("\nDOWNLOADED ✅")
            print(f"Downloaded\"{book['title']}\" by \"{book['author']}.\"")
            print(seperator)
            save()
        else:
            print("NOT FOUND ❌")
            print("Couldn't find a confident file. Try this yourself.")
            print(seperator)
            book['downloaded'] = 'not-found'
    except (ValueError, TypeError, IndexError, FileNotFoundError, AttributeError, EOFError, KeyError):
        book['downloaded'] = 'error'
        print("INTERNAL ERROR 🛑")
        print("Something came up. Try this yourself.")
        print(seperator)
        save()


def load():
    global books
    books = [eval(s.strip()) for s in open("book-list.txt").readlines()]


def save():
    global books
    target = open('book-list.txt', 'w')
    for book in books:
        target.write(str(book))
        target.write('\n')


books = None
load()


def start():
    for book in books:
        if book['downloaded'] == False:
            do_it_all(book, mirror)
        else:
            print("SKIPPED THIS BOOK ⏭")
            print(
                f"\"{book['title']}\" by \"{book['author']}\" is either downloaded or you have opted out. Moving on...")
            print(seperator)

cls()
prompt = "Select your prefered mirror.\n"
prompt += "1. Gen.lib.rus.ec\n"
prompt += "2. Libgen.lc\n> "
mirror_index = int(input(prompt))
if mirror_index == 1:
    mirror = 'gen-lib-rus-ec'
elif mirror_index == 2:
    mirror = 'libgen-lc'
else:
    pass


start()


# s = search("cal newport")
# d = decide(s)
# m = mirrors(d)
# url = mirror_to_url(m, mirror='libgen-lc')
# print(url)
