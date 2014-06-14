#!/usr/bin/env python
# -*- coding: utf-8 -*-

#     arwiki_parser -  Extract plain text from Arabic Wikipedia dumps.
#     Copyright (C) 2014  Ossama W. Obeid

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import os.path
import re

from lxml import etree
from bs4 import BeautifulSoup, Comment
from mwlib.uparser import parseString
from mwlib.dummydb import DummyDB
from mwlib.xhtmlwriter import MWXHTMLWriter, preprocess
from mwlib.xmltreecleaner import removeLangLinks


MWXHTMLWriter.ignoreUnknownNodes = False


_MIN_SIZE = 1024
bad_link_re = re.compile(
    u'^(تصنيف\:)|(تصغير)|((left\||right\|)?thumb\|(left\||right\|)?)')
diacritics_re = re.compile(u'[\u064b-\u065e]')


def noop(x, y):
    return None


def strip_diacritics(text):
    return diacritics_re.sub(text)


def extract_text(xhtml):

    if xhtml is None or len(xhtml) < _MIN_SIZE:
        return None

    soup = BeautifulSoup(xhtml)

    #Check if title refers to a mete-wiki page
    title_tag = soup.find('h1')
    if ':' in title_tag.text:
        return None
    else:
        title_tag.replace_with(title_tag.text + '\n')

    content = soup.find('div', class_="mwx.article")

    #Clean links
    links = content.find_all(['a'])
    if links is not None:
        for link in links:
            match = bad_link_re.search(link.text)
            if match is None:
                link.unwrap()
            else:
                link.decompose()

    #Remove thumbnails
    thumbs = content.find_all('div', class_='thumb')
    if thumbs is not None:
        for thumb in thumbs:
            thumb.decompose()

    #Remove publish date
    pdates = content.find_all(class_=['publish', 'published'])
    if thumbs is not None:
        for pdate in pdates:
            pdate.decompose()

    #Remove comments
    comments = content.find_all(text=lambda text: isinstance(text, Comment))
    if comments is not None:
        for comment in comments:
            comment.extract()

    #Remove hidden items
    hitems = content.find_all(class_=['noprint', 'noscript', 'mwx.reference'])

    if hitems is not None:
        for item in hitems:
            item.decompose()

    # Mark reference/see also sections for removal
    hitems = content.find_all(['h2'])
    if hitems is not None:
        for item in hitems:
            if item.text.strip() in [u'مصادر', u'مصدر', u'المصادر', u'المصدر',
                                     u'المرجع', u'مرجع', u'المراجع', u'مراجع',
                                     u'انظر أيضاً', u'طالع أيضا']:
                item.replace_with('\n>>>>> REMOVE <<<<<\n')

    # Remove titles, images, etc.
    hitems = content.find_all(['img', 'table', 'br',
                               'noscript', 'h2', 'ul',
                               'ol', 'h3', 'h4', 'h5',
                               'h6', 'mwx.gallery'])
    if hitems is not None:
        for item in hitems:
            item.replace_with('\n')

    #Unwrap all stylistic tags
    styletags = content.find_all(['i', 'b', 'span', 'small', 'center'])
    for tag in styletags:
        tag.unwrap()

    #Remove empty paragraphs, and remove newlines inside paragraphs
    pars = content.find_all('div', class_="mwx.paragaraph")
    if pars is not None:
        for par in pars:
            text = par.text.strip().replace('\n', ' ')
            if len(text) == 0:
                par.decompose()
            else:
                par.replace_with(text)
                par.append('\n')

    # Remove empty files and delete content after bibliography or see-also
    lines = content.text.strip().split('\n')
    if lines is None or len(lines) == 0:
        return None

    res = []
    for line in lines:
        line = line.strip()
        if len(line) == 0:
            continue
        elif line.strip() == ">>>>> REMOVE <<<<<":
            break
        else:
            res.append(line)

    return '\n'.join(res)


def getXHTML(wikitext, title, language):
    db = DummyDB()
    db.normalize_and_get_page = noop
    r = parseString(title=title, raw=wikitext, wikidb=db, lang=language)
    if not r:
        return None
    preprocess(r)
    removeLangLinks(r)
    dbw = MWXHTMLWriter()
    dbw.writeBook(r)
    return dbw.asstring()


def parseWikiXML(dumppath, outdir, language):
    with open(dumppath, 'r') as infile:
        xmlroot = None
        docID = None
        docTitle = None
        docText = None
        inRev = False
        firstIter = True
        tagNdx = 0

        for event, element in etree.iterparse(infile, events=("start", "end")):

            if firstIter:
                tagNdx = element.tag.rfind('}') + 1
                firstIter = False

            if element.tag[tagNdx:] == "mediawiki" and event == "start":
                xmlroot = element

            elif element.tag[tagNdx:] == "page" and event == "end":

                try:
                    xhtml = getXHTML(docText, docTitle, language)
                except:
                    xhtml = None

                try:
                    plain_text = extract_text(xhtml)
                except:
                    plain_text = None

                if xhtml is None or plain_text is None or\
                   len(plain_text) < _MIN_SIZE:
                    print ">>> Skipping article with title"\
                          "'%s' and ID '%s'" %\
                          (docTitle.encode('utf-8'), docID.encode('utf-8'))
                    xmlroot.clear()
                    continue

                docSubDir = os.path.join(outdir, hex(hash(docTitle) % 256)[2:])

                if not os.path.exists(docSubDir):
                    os.makedirs(docSubDir)

                outpath = os.path.join(docSubDir, "%s.txt" % (docID,))
                with open(outpath, 'w') as outfile:
                    outfile.write(plain_text.encode('utf-8'))

                xmlroot.clear()

            elif element.tag[tagNdx:] == "revision":
                if event == "start":
                    inRev = True
                else:
                    inRev = False

            elif element.tag[tagNdx:] == "id" and event == "end" and not inRev:
                docID = element.text
                if docID is not None and not isinstance(docID, unicode):
                    docID = docID.decode('utf-8')

            elif element.tag[tagNdx:] == "title" and event == "end":
                docTitle = element.text
                if docTitle is not None and not isinstance(docTitle, unicode):
                    docTitle = docTitle.decode('utf-8')

            elif element.tag[tagNdx:] == "text" and event == "end":
                docText = element.text
                if docText is not None and not isinstance(docText, unicode):
                    docText = docText.decode('utf-8')


def main(args):
    parseWikiXML(args[0], args[1], 'ar')


if __name__ == '__main__':
    main(sys.argv[1:])
