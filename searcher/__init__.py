import re
import io
import sqlite3
import os
from os.path import isfile, join
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from six import StringIO
import textract


class Match:
    def __init__(self,file,page,charStart,charEnd):
        self.file=file
        self.page=page
        self.charStart=charStart
        self.charEnd = charEnd


def getAllFiles(pathToApp):
    pathToDoc=pathToApp+'/static/documents'
    onlyfiles = [f for f in os.listdir(pathToDoc) if isfile(join(pathToDoc, f))]
    print(onlyfiles)
    allpdfs=[]
    for file in onlyfiles:
        if(file!='.DS_Store'):
            allpdfs.append(file)
    return allpdfs


def search_in_all_files(allFiles,searchFor):
    matches={}

    for file,props  in allFiles.items():
        if ".pdf" in file:
            search_text_in_pdf(props['location'],searchFor,matches)
        elif ".docx" in file:
            search_text_in_word(props['location'], searchFor, matches)

    return matches

def search_content_in_db(allFiles,searchFor):
    matches={}
    conn = sqlite3.connect(os.curdir+'/static/' +'documents.db')

    cur = conn.cursor()
    searchFor=searchFor.replace(" ","_")
    cur.execute("SELECT path FROM file_contents WHERE content LIKE '%"+searchFor+"%'")

    rows = cur.fetchall()

    for row in rows:
        matches[row[0]]='found'

    return matches


def search_text_in_pdf(path,searchFor,matches):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    pageIndex=0
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
        text = retstr.getvalue()
        search_word = searchFor
        searchResults = re.search(search_word, text, re.IGNORECASE)
        if searchResults:
            for reg in searchResults.regs:
                if path in matches:
                    matches[path].append({'page': pageIndex, 'startChar': reg[0], 'startChar': reg[0], 'endChar': reg[0]})
                else:
                    matches[path]=[{'page':pageIndex,'startChar':reg[0],'startChar':reg[0],'endChar':reg[0]}]
        pageIndex=pageIndex+1
        retstr.truncate(0)
        retstr.seek(0)

    fp.close()
    device.close()
    retstr.close()
    return text


def readPDF(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    text=""

    pageIndex=0
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
        text =text+" "+ retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text

def search_text_in_word(path,searchFor,matches):

    document_text = textract.process(path)
    if searchFor in str(document_text):
        matches[path] = [{'page': 0, 'startChar': 0, 'startChar': 0, 'endChar': 0}]
    matches


def doc_table_Exist(c):


    # get the count of tables with the name
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='file_contents' ''')

    # if the count is 1, then table exists
    if c.fetchone()[0] == 1:
        return True
    else:
        return False




def store_Document_in_Db(path_to_Doc, file_text):
    conn = sqlite3.connect(os.curdir+'/static/' +'documents.db')
    c = conn.cursor()
    if not doc_table_Exist(c):
        
        # Create table
        c.execute('''CREATE TABLE file_contents
                     (path TEXT, content TEXT)''')

    if file_in_table(path_to_Doc,c):
        remove_record(path_to_Doc,c)
        # Save (commit) the changes
        conn.commit()
    file_text=str(file_text)
    file_text=file_text.replace("'","''")
    # Insert a row of data
    c.execute("INSERT INTO file_contents VALUES ('"+path_to_Doc+"','"+file_text+"')")

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()
    pass


def store_PDF(path_to_Doc):
    file_text= readPDF(path_to_Doc)
    store_Document_in_Db(path_to_Doc,str(file_text))


def readWord(path_to_Doc):
    document_text = textract.process(path_to_Doc)
    return document_text


def store_Word(path_to_Doc):
    file_text = readWord(path_to_Doc)
    store_Document_in_Db(path_to_Doc, file_text)


def addToDB(path_to_Doc):
    if ".pdf" in path_to_Doc:
        store_PDF(path_to_Doc)
    elif ".docx" in path_to_Doc:
        store_Word(path_to_Doc)
    return None


def file_in_table(fileToRemove, c):
    # get the count of tables with the name
    c.execute("SELECT  path FROM file_contents WHERE path like '%"+fileToRemove+"'")

    result=c.fetchone()

    if result:
        return True
    else:
        return False
    pass


def remove_record(fileToRemove, c):
    c.execute("DELETE FROM file_contents WHERE path like '%"+fileToRemove+"%'")
    pass


def remove_from_db(fileToRemove):
    conn = sqlite3.connect(os.curdir + '/static/' + 'documents.db')
    c = conn.cursor()

    if file_in_table(fileToRemove,c):
        remove_record(fileToRemove,c)
        # Save (commit) the changes
        conn.commit()

    conn.close()
    return None