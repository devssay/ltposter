import re

def normalize_author(author):
    return re.sub('[^a-z]+', '', author.lower())

import urlparse
import httplib

def find_redirect(url):
    _, host, path, _, _ = urlparse.urlsplit(url)
    connection = httplib.HTTPConnection(host)
    connection.request('HEAD', path)
    response = connection.getresponse()
    if response.status == httplib.OK:
        return url
    assert response.status == httplib.FOUND
    location = response.getheader('Location')
    redirect = urlparse.urljoin(url, location)
    if 'search_works.php' in redirect:
        return
    return redirect

def link_author(author):
    author = normalize_author(author)
    url = 'http://www.librarything.com/author/' + author
    return find_redirect(url)

# http://www.librarything.com/blog/2006/07/new-ways-to-link-to-book.php
def link_isbn(isbn):
    url = 'http://www.librarything.com/isbn/' + isbn
    return find_redirect(url)

def link_title(title):
    title = urllib.quote(title)
    url = 'http://www.librarything.com/title/' + title
    return find_redirect(url)

def get_lastpart(url):
    return url.rsplit('/', 1)[1]

import urllib
import elementtree.ElementTree as ET

# http://www.librarything.com/thingology/2006/06/introducing-thingisbn_14.php
def thingISBN(isbn):
    url = 'http://www.librarything.com/api/thingISBN/' + isbn
    tree = ET.parse(urllib.urlopen(url))
    if tree.find('unknownID') is not None:
        return False
    return True

# http://www.librarything.com/thingology/2006/08/thinglang.php
def thingLang(isbn):
    url = 'http://www.librarything.com/api/thingLang.php?isbn=' + isbn
    code = urllib.urlopen(url).read()
    return code

# Codes below this point are reverse-engineered from HTML

import cookielib
import urllib2
import BeautifulSoup

def signup(username, password):
    url = 'http://www.librarything.com/signup.php'
    jar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
    params = dict(
        formusername=username,
        formpassword=password)
    result = opener.open(url, urllib.urlencode(params))
    if 'problem' in result.geturl():
        return
    if 'failed' in result.geturl():
        return
    return LTAccount(opener)

class LTAccount(object):

    def __init__(self, opener):
        self.opener = opener

    def run(self, url, params):
        self.opener.open(url, urllib.urlencode(params))

    def update(self, title, author, date, isbn, publication, lang):
        url = 'http://www.librarything.com/update.php'
        params = dict(
            form_title=title,
            form_authorunflip=author,
            form_ISBN=isbn,
            form_date=date,
            form_publication=publication,
            field_lang=lang,
            form_id='NEW')
        self.run(url, params)

    def get_bookid(self, isbn):
        url = 'http://www.librarything.com/catalog_bottom.php?searchbox=' + isbn
        response = self.opener.open(url)
        soup = BeautifulSoup.BeautifulSoup(response)
        coverid = soup.find('td', 'cover')['id']
        return str(coverid[5:])

    def set_cover(self, bookid, cover):
        url = 'http://www.librarything.com/addcover_upload.php'
        params = dict(
            form_url=cover,
            grab='1',
            book=bookid)
        self.run(url, params)

    def work_combine(self, author, work1, work2):
        url = 'http://www.librarything.com/work_combineworks_submit.php'
        work = '%s/%s' % (work1, work2)
        params = dict(
            combine=work,
            author=author)
        self.run(url, params)
