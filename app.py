import sqlite3
import base64
import configparser

import requests
from flask import Flask, g, render_template, abort

import database

config = configparser.ConfigParser()
config.read('config.ini')
DATABASE_PATH = config.get('DATABASE', 'PATH')


app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_PATH)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index_cat():
    # TODO return cat picture and id
    get_picture = requests.get('https://api.thecatapi.com/v1/images/search')  # Get picture
    url_pic = get_picture.json()[0]["url"]  # Get picture url from json
    id_pic = get_picture.json()[0]["id"]  # Get picture id from json
    base64_pic = base64.b64encode(requests.get(url_pic).content).decode("UTF-8")

    cur = get_db().cursor()  # Connect to db
    database.add_cat_to_bd(base64_pic, id_pic, cur)  # Add new record to db
    get_db().commit()  # Commit changes
    return render_template('index.html', data=base64_pic)


@app.route('/<cat_id>/')
def get_cat_by_id(cat_id):
    # TODO return cat picture by id if exists

    cur = get_db().cursor()
    url = database.find_cat_id(cat_id, cur)  # Try to find cat_id in db
    if url is None:
        abort(404)  # If database doesn't have url return 404
    else:
        return render_template('index.html', data=url[0])


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html'), 404


if __name__ == '__main__':
    database.create_db()  # Will create database if not exists
    app.run()
