import urllib
import elementtree.ElementTree as ET
import isbntool

# http://dna.daum.net/apis
class DNA(object):

    # Seo Sanghyeon's key. Daum ID mathmaniac.
    defaultKey = 'bb3b53838b4f980367c230baf132958de15a98a9'

    def __init__(self, key=None):
        if key:
            self.key = key
        else:
            self.key = self.defaultKey

    # http://dna.daum.net/apis/search/book
    def book(self, isbn):
        isbn10 = isbntool.convert_to_10(isbn)
        query = {}
        query['apikey'] = self.key
        query['target'] = 'meta'
        query['q'] = ''
        query['isbn'] = isbn10
        url = 'http://apis.daum.net/search/book?' + urllib.urlencode(query)
        tree = ET.parse(urllib.urlopen(url))
        element = tree.find('item')
        if element is not None:
            return DaumBook(element)

class DaumBook(object):

    def __init__(self, element):
        self.element = element

    def get(self, tag):
        element = self.element.find(tag)
        if element is not None:
            return element.text

    def cover(self):
        return self.get('cover_l_url')

    def author(self):
        return self.get('author')

    def translator(self):
        return self.get('translator')
