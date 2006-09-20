import urllib
import elementtree.ElementTree as ET

# http://openapi.naver.com/
class NaverOpenAPI(object):

    # Seo Sanghyeon's key. Naver ID sanxiyn.
    defaultKey = 'b2730786365fd6614977e2a4ae265b91'

    def __init__(self, key=None):
        if key:
            self.key = key
        else:
            self.key = self.defaultKey

    # http://openapi.naver.com/05.html
    def book(self, isbn):
        query = {}
        query['key'] = self.key
        query['target'] = 'book_adv'
        query['query'] = ''
        query['d_isbn'] = isbn
        url = 'http://openapi.naver.com/search?' + urllib.urlencode(query)
        tree = ET.parse(urllib.urlopen(url))
        element = tree.find('channel/item')
        if element is not None:
            return NaverBook(element)

class NaverBook(object):

    def __init__(self, element):
        self.element = element

    def get(self, tagname):
        element = self.element.find(tagname)
        if element is not None:
            return element.text.strip()

    def cover(self):
        return self.get('image')

    def title(self):
        return self.get('title')

    def date(self):
        pubdate = self.get('pubdate')
        pubyear = pubdate[:4]
        return pubyear

    def publication(self):
        publisher = self.get('publisher')
        pubyear = self.date()
        publication = '%s (%s)' % (publisher, pubyear)
        return publication
