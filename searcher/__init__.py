import re
import io
from os import listdir
from os.path import isfile, join
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from six import StringIO


class Match:
    def __init__(self,file,page,charStart,charEnd):
        self.file=file
        self.page=page
        self.charStart=charStart
        self.charEnd = charEnd


def getAllFiles(pathToApp):
    pathToDoc=pathToApp+'/static/documents'
    onlyfiles = [f for f in listdir(pathToDoc) if isfile(join(pathToDoc, f))]
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

