import urlparse
import httplib

def check(url):
    _, host, path, _, _ = urlparse.urlsplit(url)
    connection = httplib.HTTPConnection(host)
    connection.request('HEAD', path)
    response = connection.getresponse()
    if response.status == httplib.NOT_FOUND:
        return False
    return True

def cover(isbn):
    prefix = 'http://image.aladdin.co.kr/cover/cover/'
    url1 = prefix + isbn + '_1.gif'
    url2 = prefix + isbn + '_1.jpg'
    if check(url1):
        return url1
    if check(url2):
        return url2
