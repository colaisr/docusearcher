import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, jsonify, send_file
from os import listdir,curdir
from os.path import isfile, join,getmtime
import os
import searcher

app = Flask(__name__)
app.secret_key = 'h432hi5ohi3h5i5hi3o2hi'


def get_all_documents():
    """ Returns the dictionary of all files"""
    pathToDoc=curdir+'/static/documents'
    if not os. path. isdir(pathToDoc):
        os.mkdir(pathToDoc)

    f=listdir(pathToDoc)
    onlyfiles = [f for f in listdir(pathToDoc) if isfile(join(pathToDoc, f))]
    allpdfs={}
    for file in onlyfiles:
        if(file!='.DS_Store'):
            fileDate = datetime.datetime.fromtimestamp(os.path.getctime(os.path.join(pathToDoc, file))).date()
            allpdfs[file]={'location':pathToDoc+'/'+file,'uploadedAt':fileDate}
    return allpdfs


@app.route('/documents')
def documents():
    files=get_all_documents()
    return render_template('documents.html', files=files)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/search', methods=['POST'])
def search():
    searchFor=request.form['phrase']

    results=searcher.search_content_in_db(get_all_documents(),searchFor)
    if not bool(results):
        results='empty'
    return render_template('searchresults.html',searched=searchFor,results=results)


@app.route('/removeDocument' , methods=['POST'])
def removeDocument():
    fileToRemove=curdir+'/static/documents/'+request.form['filename']
    os.remove(fileToRemove)
    searcher.remove_from_db(fileToRemove)
    return redirect(url_for('documents'))


@app.route('/uploaddocument', methods=['POST'])
def uploadFile():
    # f = Flask.request.files.getlist("file")
    files=request.files.getlist("file")
    for f in files:
        path_to_Doc=os.curdir+'/static/documents/' + f.filename
        f.save(path_to_Doc)
        searcher.addToDB(path_to_Doc)
        print('successfully added:'+path_to_Doc)


    return redirect(url_for('documents'))


@app.route('/getdocument/<string:file>')
def getfile(file):
    fullpath= os.curdir+'/static/documents/' + file
    return send_file(fullpath)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


if __name__ == '__main__':
    app.run()
