import sys

charset = 'utf-8'

def encode(s):
    if s:
        return s.encode(charset)
    else:
        return s

def http_header():
    header = 'Content-Type: text/html; charset=%s\r\n\r\n' % (charset,)
    sys.stdout.write(header)

def print_header(title, css=None):
    http_header()
    print ('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
           '"http://www.w3.org/TR/html4/strict.dtd">')
    print '<html>'
    print '<head>'
    print '<title>%s</title>' % (title,)
    if css:
        print '<link rel="stylesheet" type="text/css" href="%s">' % (css,)
    print '</head>'
    print '<body>'

def print_footer():
    print '</body>'
    print '</html>'

def start_table():
    print '<table><tr><td>'

def end_table():
    print '</td></tr></table>'

def next_cell():
    print '</td><td>'
