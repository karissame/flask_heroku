"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import os
import pg
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename

import sys

reload(sys)
sys.setdefaultencoding('utf8')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', True)
app.config['UPLOAD_FOLDER'] = "/Users/DSS-Mac/htdocs/flask_heroku/static/profilepics/"
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
@app.route("/")
def listings():
    setActiveTab("home")
    if session.get('username'):
        print 'You are logged in.'
        if session.get('admin') == 1:
            query = db.query("SELECT id,name,email,phone,photo_ext FROM phonebook")
        else:
            query = db.query("SELECT id,name,email,phone,photo_ext FROM phonebook WHERE created_by = %d" % int(session.get('userid')))
        result_list=query.namedresult()
        l = []
        for each in result_list:

            l.append(list(each))
        print l
        for i in l:
            print i
            if i[4]:
                print i[0]
                print i[4]
                i[4]= str(i[0]) + "." +i[4]
                print i[4]
            else:
                i[4]= "placeholder.jpg"
        print 'Showing listings now'
        return render_template("listings.html", contact_list=l, title="My Phonebook",activeTab=activeTab)
    else:
        print 'Sending you to login page'
        return render_template("login.html", activeTab=activeTab)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/update_entry")
def updateEntry(methods = ['GET']):
    id = request.args.get('id')
    print id
    print session.get('userid')
    query = db.query("SELECT id,name,email,phone,photo_ext FROM phonebook WHERE id = '%s' and created_by = '%d' " % (id,session.get('userid')))
    list = query.namedresult()
    print list
    setActiveTab("updateEntry")
    return render_template("update_entry.html", phonebook=list[0], title="My Phonebook",activeTab=activeTab)

#set all active tab dictionaries value to "" then make the indicated tab from the flask route function active. This make class="active" for css styling dynamically.
def setActiveTab(tabName):
    global activeTab
    for tab in activeTab:
        activeTab[tab] = ""
    if activeTab.has_key(tabName):
        activeTab[tabName] = "active"
    print activeTab

@app.route("/new_entry")
def new_entry():
    setActiveTab("addEntries")
    created_by = int(session.get('userid'))
    print created_by
    return render_template("new_entry.html", title="My Phonebook",activeTab=activeTab,created_by=created_by)

#check if this page is being reached from a POST. If not, ignore functions. Otherwise check filename is safe, grab the ext of the image file for storage in the db and insert new entry.
#After entry is stored, get the new id from db and use it plus '.' plus ext to save the image to the server.
@app.route("/submit_new_entry", methods=['POST'])
def submit_new_student():
    setActiveTab("addEntries")
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print filename
            ext = filename.lower().rsplit('.', 1)[1]
        else:
            ext = ""
        print ext
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        created_by=session.get('userid')
        print created_by
        query = db.query("insert into phonebook (name,email,phone,photo_ext,created_by) values ('%s','%s','%s','%s','%d') RETURNING id" % (Database.escape(name),Database.escape(email),Database.escape(phone),Database.escape(ext),created_by))
        newentry = query.namedresult()
        lastID = newentry[0].id
        print lastID
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(lastID)+"."+ext))

    # return render_template("submit_new_entry.html", name=name,email=email,phone=phone, activeTab=activeTab)
    return redirect("/")

#Need to add ability to update images. Have to move on for now. To do: Extract image upload with overwrite to an outsidefunction either new_contact or update_contact can make use of.
@app.route("/submit_update_contact", methods=['POST'])
def submit_update_contact():
    id = request.form.get('id')
    setActiveTab("updateEntry")
    name=request.form.get('name')
    email=request.form.get('email')
    phone=request.form.get('phone')
    if request.form['submit'] == 'update':
        query = db.query("UPDATE phonebook SET name = '%s', email = '%s', phone = '%s' WHERE id = '%s'" % (Database.escape(name),Database.escape(email),Database.escape(phone), id))
    if request.form['submit'] == 'delete':
        query = db.query("DELETE FROM phonebook WHERE id = '%s'" % id)
    return redirect("/")

@app.route('/submit_login', methods=['POST'])
def submit_login():
    username = request.form.get('username')
    password = request.form.get('password')
    query = db.query("select * from myuser where username = '%s'" % Database.escape(username))
    result_list = query.namedresult()
    print result_list
    # if result_list:
    #     result = result_list[0]
    #     username = result.username
    #     if result.password == Database.escape(password):
    #         # successfully logged in
    #         session['username'] = username
    #         session['userid'] = result.id
    #         session['admin'] = result.admin
    return redirect('/')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

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
