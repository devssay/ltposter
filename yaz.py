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
# http://www.nl.go.kr/kormarc/regulation/regulation0301.htm
class MARCRecord(object):

    def __init__(self, dic):
        self.dic = dic

    def author(self):
        value = self.dic.get('100a')
        if value is None:
            return
        if value[-1] == ',':
            value = value[:-1]
        return value

    def original_title(self):
        value = self.dic.get('507t')
        if value is None:
            return
        if value[:3] == '(A)':
            value = 'A ' + value[3:]
        if value[:5] == '(The)':
            value = 'The ' + value[5:]
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
