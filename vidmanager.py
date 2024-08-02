#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for
import os
import shutil
import json
selectedpath = '00_selected'
app = Flask(__name__)

# Load configuration

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.json')) as config_file:
    config = json.load(config_file)
BASE_FOLDER = config['base_folder']
PORT = config.get('port', 5000)


@app.route('/')
@app.route('/<path:subpath>')
def index(subpath=''):
    current_folder = os.path.join(BASE_FOLDER, subpath)
    if not os.path.exists(current_folder):
        return "Folder not found.", 404

    files = os.listdir(current_folder)
    folders = sorted([f for f in files if os.path.isdir(os.path.join(current_folder, f))])
    # don´t show m3u8 files
    files = sorted([f for f in files if os.path.isfile(os.path.join(current_folder, f)) and not f.lower().endswith('.m3u8')]) 
    parent_folder = os.path.dirname(subpath)
# I hate having the template in a separate file, in HTML. Can it be built dynamically?
    return render_template('index.html', folders=folders, files=files, subpath=subpath, parent_folder=parent_folder, os=os)

# there should be a "star" option to mark some folders/files as interesting. 
# this could also be a "category" option and we could group the files by category on the page


@app.route('/archive', methods=['POST'])
def archive():
# if in the 00_selected folder, move it to the base folder without the 00_selected
# if in the base folder, move it to the 00_Archive folder    
    subpath = request.form['subpath']
    name = request.form['name']
    item_path = os.path.join(BASE_FOLDER, subpath, name)
    archive_folder = os.path.join(BASE_FOLDER, subpath, '00_Archive')

    if not os.path.exists(archive_folder):
        os.makedirs(archive_folder)

    if os.path.exists(os.path.join(archive_folder, name)):
        if os.path.isfile(os.path.join(archive_folder, name)) or os.path.islink(os.path.join(archive_folder, name)):
            os.remove(os.path.join(archive_folder, name))
        elif os.path.isdir(os.path.join(archive_folder, name)):
            shutil.rmtree(os.path.join(archive_folder, name))
    shutil.move(item_path, os.path.join(archive_folder, name))

    return redirect(url_for('index', subpath=subpath))


@app.route('/later', methods=['POST'])
def later():
    subpath = request.form['subpath']
    name = request.form['name']
    item_path = os.path.join(BASE_FOLDER, subpath, name)
    later_folder = os.path.join(BASE_FOLDER, subpath, '00_later')
    later_fullname = os.path.join(later_folder, name)
    if not os.path.exists(later_folder):
        os.makedirs(later_folder)

    if os.path.exists(later_fullname):
        if os.path.isfile(later_fullname) or os.path.islink(later_fullname):
            os.remove(later_fullname)
        elif os.path.isdir(later_fullname):
            shutil.rmtree(later_fullname)
    shutil.move(item_path, later_fullname)

    return redirect(url_for('index', subpath=subpath))


@app.route('/select', methods=['POST'])
def select():
    subpath = request.form['subpath']
    name = request.form['name']
    item_path = os.path.join(BASE_FOLDER, subpath, name)
    selected_folder = os.path.join(BASE_FOLDER, selectedpath)
    selected_fullname = os.path.join(selected_folder, name) 
    archive_folder = os.path.join(BASE_FOLDER,  subpath, '00_Archive')
    archive_fullname = os.path.join(archive_folder, name)

    if not os.path.exists(selected_folder):
        os.makedirs(selected_folder)

    if not os.path.exists(archive_folder):
        os.makedirs(archive_folder)

    if os.path.exists(item_path):
        if not os.path.exists(selected_fullname):
            if os.path.isfile(item_path) or os.path.islink(item_path):
                shutil.copy(item_path, selected_fullname,follow_symlinks=False)
            elif os.path.isdir(item_path):
                shutil.copytree(item_path, selected_fullname,symlinks=True)


            
        if os.path.exists(archive_fullname):
            if os.path.isfile(archive_fullname) or os.path.islink(archive_fullname):
                os.remove(archive_fullname)
            elif os.path.isdir(archive_fullname):
                shutil.rmtree(archive_fullname)
        shutil.move(item_path, archive_fullname)

    return redirect(url_for('index', subpath=subpath))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
