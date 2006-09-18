#!/usr/bin/python2.4
# vim:encoding=utf-8:

import cgitb
cgitb.enable()

import sys
import os
import cgi

import cgiutil
import isbntool
import ltapi
import naver
import aladdin
import zinfo
import yaz
import account

import useragent
useragent.install()

def isbn_form():
    cgiutil.print_header('ISBN 검색', 'style.css')
    print '<form action="lt.cgi" method="get">'
    print '<p>'
    print '<label for="isbn">ISBN</label>'
    print '<input name="isbn" id="isbn" size="10">'
    print '<input type="submit" value="검색">'
    print '</p>'
    print '</form>'
    print '<p>'
    print '<a href="demo/demo1.html">데모 버전 보기</a>'
    print '</p>'
    cgiutil.print_footer()

def return_link():
    print '<p>'
    print '<a href="lt.cgi">검색으로 돌아갑니다</a>.<br>'
    print '</p>'

def isbn_query(isbn):
    title = 'ISBN 검색: %s' % (isbn,)
    cgiutil.print_header(title, 'style.css')
    print '<form action="lt.cgi" method="post">'
    cgiutil.start_table()
    do_isbn_query(isbn)
    return_link()
    cgiutil.end_table()
    print '</form>'
    cgiutil.print_footer()

def hidden_input(key, value):
    print '<input type="hidden" name="%s" value="%s">' % (key, value)

def print_info(key, value, hkey=None):
    print '<span class="info">%s %s.</span><br>' % (key, value)
    if hkey:
        hidden_input(hkey, value)

def print_progress(text):
    print '<span class="progress">%s...</span><br>' % (text,)
    sys.stdout.flush()

def do_isbn_query(isbn):
    print '<p>'
    print_info('ISBN', isbn, 'isbn')
    if not isbntool.validate(isbn):
        print '올바른 ISBN이 아닙니다.<br>'
        print '</p>'
        return
    lang = ltapi.thingLang(isbn)
    print_info('언어', lang, 'lang')
    print '</p>'

    print '<p>'
    print_progress('LibraryThing에 등록되어 있는지 확인합니다')

    if ltapi.thingISBN(isbn):
        url = ltapi.link_isbn(isbn)
        print '<a href="%s">이미 있습니다</a>.<br>' % (url,)
        print '</p>'
        return
    else:
        print '아직 없습니다.<br>'
        print '</p>'

    print '<p>'
    print_progress('네이버에서 책 정보를 검색합니다')

    api = naver.NaverOpenAPI(account.naverkey)
    book = api.book(isbn)
    if book:
        title = book.title().encode('utf-8')
        publication = book.publication().encode('utf-8')
        print_info('제목', title, 'title')
        print_info('출판사', publication, 'publication')
        print '</p>'
    else:
        print '없습니다.<br>'
        print '</p>'
        return

    print '<p>'
    print_progress('책 표지를 검색합니다')

    cover = None
    naver_cover = book.cover()
    if naver_cover:
        print '네이버'
        print '<img src="%s" alt="네이버 표지">' % (naver_cover,)
        cover = naver_cover
    aladdin_cover = aladdin.cover(isbn)
    if aladdin_cover:
        print '알라딘'
        print '<img src="%s" alt="알라딘 표지">' % (aladdin_cover,)
        cover = aladdin_cover
    print '<br>'
    if cover:
        hidden_input('cover', cover)
    print '</p>'

    cgiutil.next_cell()

    original_title = None
    for server in zinfo.servers:
        result = z3950_query(server, isbn)
        if result:
            original_title, author = result
            break
    if not original_title:
        return

    print '<p>'
    print_progress('원서명으로 LibraryThing을 검색합니다')

    url = ltapi.link_title(original_title)
    if url:
        print '<a href="%s">%s</a>' % (url, original_title),
        author_url = ltapi.link_author(author)
        print 'by <a href="%s">%s</a>.<br>' % (author_url, author)
        hidden_input('workid', ltapi.get_lastpart(url))
        hidden_input('authorid', ltapi.get_lastpart(author_url))
        print '</p>'
    else:
        print '없습니다.<br>'
        print '</p>'
        return

    print '<p>'
    print '<input type="submit" value="등록">'
    print '</p>'

def z3950_query(server, isbn):
    name, zurl, charset, dir = server

    print '<p>'
    print_progress(name + '에서 원서명과 원저자명을 검색합니다')

    api = yaz.YAZ(zurl, charset, dir)
    book = api.get(isbn)
    if not book:
        print '없습니다.<br>'
        print '</p>'
        return
    original_title = book.original_title()
    author = book.author()
    if original_title and author:
        print_info('원서명', original_title)
        print_info('원저자명', author, 'author')
        print '</p>'
    else:
        print '번역된 책이 아닙니다.'
        print '</p>'
        return

    return original_title, author

def isbn_post(form):
    cgiutil.print_header('책 등록', 'style.css')
    print '<p>'
    print_progress('LibraryThing에 로그인합니다')
    api = ltapi.signup(account.username, account.password)
    if not api:
        print '실패했습니다.<br>'
        print '</p>'
        return
    title = form.getvalue('title')
    author = form.getvalue('author')
    isbn = form.getvalue('isbn')
    publication = form.getvalue('publication')
    lang = form.getvalue('lang')
    print_progress('책을 등록합니다')
    api.update(title, author, isbn, publication, lang)
    print_progress('방금 등록한 책의 ID를 가져옵니다')
    bookid = api.get_bookid(isbn)
    print_info('bookid', bookid)
    print_progress('표지를 올립니다')
    cover = form.getvalue('cover')
    api.set_cover(bookid, cover)
    print_progress('책을 원서와 엮을 준비를 합니다')
    authorid = form.getvalue('authorid')
    workid = form.getvalue('workid')
    thisid = ltapi.get_lastpart(ltapi.link_isbn(isbn))
    print_info('authorid', authorid)
    print_info('workid', workid)
    print_info('thisid', thisid)
    print_progress('책을 엮습니다')
    api.work_combine(authorid, workid, thisid)
    url = 'http://www.librarything.com/work-info/%s&book=%s' % (workid, bookid)
    print '<a href="%s">등록되었습니다</a>.<br>' % (url,)
    print '</p>'
    return_link()
    cgiutil.print_footer()

if __name__ == '__main__':
    form = cgi.FieldStorage()
    method = os.environ['REQUEST_METHOD']
    if method == 'GET':
        if form.has_key('isbn'):
            isbn = form.getvalue('isbn')
            isbn_query(isbn)
        else:
            isbn_form()
    elif method == 'POST':
        isbn_post(form)
