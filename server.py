
import os

from werkzeug.utils import secure_filename

from jinja2 import StrictUndefined

from flask import (g, Flask, render_template, redirect, request, flash, session, url_for, send_from_directory)
from flask_debugtoolbar import DebugToolbarExtension
from functools import wraps

from model import Video, User, connect_to_db, db

from datetime import datetime


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

#Make sure jinja tells you if you're using an undifined variable
app.jinja_env.undefined = StrictUndefined

######################################################################################################################################
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # if g.user is None:
        user_id = session['user_id']
        if user_id == None:
            # return redirect('/login')
            return redirect(url_for('/login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
# @login_required
def homepage():
    """render homepage"""
    videos = Video.query.order_by(Video.date_uploaded.desc()).all()

    return render_template('homepage.html', videos=videos)



@app.route('/login')
def login_form():
    """render login form"""

    return render_template('login_form.html')


@app.route('/login-check', methods=["POST"])
def check_login_info():
    """check login info from login form"""

    username = request.form.get('username')
    username = username.lower()
    password = request.form.get('password')

    #query database to see if username entered exists
    user_info = User.query.filter(User.username==username).first()

    if user_info is None:
        #Suggest create profile or check username

        flash("""Ooops. The username you entered isn't in our database. 
                    Are you sure you entered it correctly? Do you want to
                    create a profile?""")
        return redirect('/login')

    elif user_info.password == password:
        #add user's info to session and redirect to homepage

        flash("You're logged in!")
        session['user_id'] = user_info.user_id
        return redirect('/')

    else:
        #suggest they check their password
        flash("Ooops. Looks like you entered your password incorrectly.")
        return redirect('/login')

@app.route('/logout')
def logout_user():
    """render logout template"""

    return render_template('logout.html')


@app.route('/logout-check')
def logout_check():
    """delete username from session if they want to logout"""
    del session['user_id']

    flash("You're logged out. See you next time.")
    return redirect('/')


@app.route('/add-user-form')
def add_user_form():
    """show form to add new user"""

    return render_template('add_user.html')


@app.route('/add-user', methods=['POST'])
def add_user():
    """add new user to database"""

    #get info entered from form
    name = request.form.get('name')
    name = name.lower()

    username = request.form.get('username')
    username = username.lower()

    email = request.form.get('email')
    email = email.lower()
    
    password = request.form.get('password')

    #check if the username is already taken
    user_check = User.query.filter(User.username==username).first()

    if user_check == None:

        #add info to database and redirect to homepage if username is available
        flash('Welcome!')

        user = User(name=name, username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.user_id

        return redirect('/')
    
    else:
        #suggest trying a different username if it's already being used
        flash('Sorry, that username is taken. Try another')
        return redirect('/add-user-form')

@app.route('/profile')
def user_profile():
    """Show users videos on profile page"""
    user_id = session['user_id']

    user = User.query.filter(User.user_id == user_id).first()
    username = user.name.capitalize()

    videos = Video.query.filter(Video.user_id==user_id).order_by(Video.video_id.desc()).all()

    return render_template('profile.html', videos=videos, username=username)

######################################################################################################################################
#video-upload functions

UPLOAD_FOLDER = './static/uploads'

ALLOWED_EXTENSIONS = set(['webm', 'mkv', 'flv', 'vob', 'ogv', 'ogg', 'drc', 'gif', 'gifv', 'mng', 'avi',
                         'mov', 'qt', 'wmv', 'yuv', 'rm', 'amv', 'mp4', 'm4p', 'm4v', 'f4v', 'f4p', 'f4a', 'f4b'])

# app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/video-upload')
def upload_file_form():
    """Show form to upload a video"""

    return render_template('video_upload_form.html')


@app.route('/video-upload-submit', methods=['GET', 'POST'])
def upload_file():
    """Upload video and save file to uploads folder"""

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect('/video-upload')

        file = request.files['file']

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect('/video-upload')

        if file and allowed_file(file.filename):
            #find file extension
            filename = secure_filename(file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower()

            #create new file name using user_id, file_ext, and date_uploaded

            user_id = session['user_id']
            video_num = Video.query.filter(Video.user_id == user_id).count()
            video_num = video_num + 1

            filename = str(user_id) + '_' + str(video_num) + '.' + file_ext
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            #add video to database
            date_uploaded = datetime.now()
            video = Video(user_id=user_id, date_uploaded =date_uploaded , filename=filename)

            db.session.add(video)
            db.session.commit()

            return redirect('/video-upload/{}'.format(filename))

    else:
        flash("oops. Something went wrong. Check the file extension on your file")
        return redirect('/video-upload')

    #this was the original else return:
    # '''
    # <!doctype html>
    # <title>Upload new File</title>
    # <h1>Upload new File</h1>
    # <form method=post enctype=multipart/form-data>
    #   <input type=file name=file>
    #   <input type=submit value=Upload>
    # </form>
    # '''

@app.route('/video-upload/<filename>')
def show_video_details(filename):
    """Show details for a given video"""

    video = Video.query.filter(Video.filename == filename).first()

    return render_template('video_details.html', video = video)






######################################################################################################################################
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app, 'postgres:///project')

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.run(port=5000, host='0.0.0.0')