# coding: utf-8

import os
import time
from subprocess import Popen, PIPE
import elementtree.ElementTree as ET

NULL = open('/dev/null')

# http://www.loc.gov/standards/marcxml/
def MARCXML(tag):
    return '{http://www.loc.gov/MARC21/slim}' + tag

# man yaz-marcdump
class MARC(object):

    def __init__(self, charset):
        self.charset = charset

    def parse(self, path):
        tree = self.get_tree(path)
        dic = self.parse_tree(tree)
        return MARCRecord(dic)

    def get_tree(self, path):
        proc = Popen(['yaz-marcdump', '-X',
            '-f', self.charset, '-t', 'UTF-8', path],
            stdout=PIPE, stderr=NULL)
        filter = Popen(['grep', '-v', '^Bad Length'],
            stdin=proc.stdout, stdout=PIPE)
        tree = ET.parse(filter.stdout)
        return tree

    def parse_tree(self, tree):
        dic = {}
        for field in tree.findall(MARCXML('datafield')):
            for subfield in field.findall(MARCXML('subfield')):
                tag = field.get('tag')
                code = subfield.get('code')
                key = tag + code
                value = subfield.text
                dic[key] = value
        return dic

# MARC
# http://www.loc.gov/marc/bibliographic/
# KS X 6006-2, KORMARC
# http://www.nl.go.kr/kormarc/regulation/regulation0301source.htm

# 본서명과 대등서명에 정관사나 부정관사가 있는 경우에는 이를 원괄호로
# 묶어 기술한다.
def filter_article(article, title):
    parened = '(' + article + ')'
    l = len(parened)
    if article[-1] != "'":
        article = article + ' '
    if title[:l] == parened:
        return article + title[l:]
    return title

def filter_words(stopwords, title):
    words = title.split()
    filtered = [word for word in words if word not in stopwords]
    return ' '.join(filtered)

class MARCRecord(object):

    def __init__(self, dic):
        self.dic = dic

    def get(self, *tags):
        for tag in tags:
            value = self.dic.get(tag)
            if value is not None:
                return value

    def lang(self):
        return self.get('041a')

    def original_lang(self):
        return self.get('041h')

    # 507 원저자, 원서명에 관한 주기 (Original Author, Original Title Note)
    # 이 필드에는 번역자료의 원저자명과 원서명을 기술한다.

    def author(self):
        value = self.get('507a', '100a')
        if value is None:
            return
        if value[-1] == ',':
            value = value[:-1]
        return value

    articles = ['A', 'The', 'Il', "L'", 'La', 'Les', 'Le']
    stopwords = ['&']

    def original_title(self):
        value = self.dic.get('507t')
        if value is None:
            return
        for article in self.articles:
            value = filter_article(article, value)
        value = filter_words(self.stopwords, value)
        if ':' in value:
            value = value.split(':', 1)[0].strip()
        return value

# man yaz-client
class YAZ:

    def __init__(self, zurl, charset, dir):
        self.proc = Popen(['yaz-client', zurl],
            stdin=PIPE, stdout=NULL)
        self.marc = MARC(charset)
        self.dir = dir
        if not os.path.exists(dir):
            os.mkdir(dir)
            os.chmod(dir, 0777)

    def path(self, isbn):
        return os.path.join(self.dir, isbn)

    def get(self, isbn):
        path = self.path(isbn)
        if not os.path.exists(path):
            pipe = self.proc.stdin
            pipe.write('set_marcdump %s\n' % path)
            pipe.write('find @attr 1=7 %s\n' % isbn)
            pipe.write('show\n')
            while not os.path.exists(path):
                time.sleep(1)
        if not os.path.getsize(path):
            os.remove(path)
            return
        result = self.marc.parse(path)
        return result
