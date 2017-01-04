"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import os
import pg
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

import sys

reload(sys)
sys.setdefaultencoding('utf8')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')
app.config['UPLOAD_FOLDER'] = "/Users/DSS-Mac/htdocs/myPhonebook/static/profilepics/"
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
home_dir = os.path.join(app.config['UPLOAD_FOLDER'],"")

DBUSER=os.environ.get('DBUSER', True)
DBPASS=os.environ.get('DBPASS', True)
DBHOST=os.environ.get('DBHOST', True)
DBNAME=os.environ.get('DBNAME', True)
db=pg.DB(host=DBHOST, user=DBUSER, passwd=DBPASS, dbname=DBNAME)
###
# Routing for your application.
###
activeTab={"home":"","addEntries":"","updateEntry":""}

def allowed_file(filename):
    return '.' in filename and \
           filename.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

class Database:
    @staticmethod
    def escape(value):
        return value.replace("'","''")

#If user is logged in and admin, Grab all db entries, cast tuples to a list, then for each, check if photo_ext is anything. If so, concatenate the id, '.', and ext to generate image filename and store it as such in the new list 'l'. If no valid value, use placeholder.jpg instead for the filename.

#If user is basic user, do the same but only their entries. If not an authenticated user, redirect to login form indefinitely.

@app.route('/')
def home():
    """Render website's home page."""
    query=db.query("select * from album")
    result_list = query.namedresult()
    return render_template('home.html',result_list=result_list)





###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
