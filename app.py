from datetime import datetime
from email.policy import default
from enum import auto, unique
from fileinput import filename
from flask import Flask, render_template, request, redirect, url_for, flash
import os 
from werkzeug.utils import secure_filename
import requests
import json
from requests import post
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
import os
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

class ReCaptha():
    SECRET_KEY = 'your google recaptcha private key' 
    RECAPTCHA_USE_SSL= False
    RECAPTCHA_PUBLIC_KEY = 'your google recaptcha public key'
    RECAPTCHA_PRIVATE_KEY = 'your google recaptcha private key'
    RECAPTCHA_DATA_ATTRS = {'theme': 'light'}




def is_human(captcha_response):
    secret = "your google recaptcha private key"
    payload = {'response': captcha_response, 'secret': secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
    response_text = json.loads(response.text)
    return response_text['success']


app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'secret key'

UPLOAD_FOLDER = 'static/uploads/'


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

login_manager = LoginManager()
login_manager.login_view = 'sign_in'
login_manager.init_app(app)

app.config.from_object(ReCaptha)

pub_key = ReCaptha.RECAPTCHA_PUBLIC_KEY
private_key = ReCaptha.RECAPTCHA_PRIVATE_KEY

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), unique = False, nullable = False)
    email = db.Column(db.String(200), unique = True, nullable = False)
    password = db.Column(db.String(200), unique = False, nullable = False)
    image = db.Column(db.String(250), nullable = True)
    desc = db.Column(db.String(200), nullable = True)
    info = db.Column(db.String(1000), nullable = True)
    mob = db.Column(db.String(12), nullable = True)
    location = db.Column(db.String(50), nullable = True)
    time = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    admin = db.Column(db.Boolean, default=False)
    
    def __init__(self, name, email, password, admin):
        self.name = name
        self.email = email
        self.password = password
        self.admin = admin

    def is_authenticated(self):
        return True

    def is_admin(self):
        return False

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"Name : {self.name}"


@login_manager.user_loader
def load_user(id):
    return Profile.query.get(int(id))

@app.route('/dashboard')
@login_required
def dash():
    return render_template('dashboard.html', user=current_user, active=True)


@app.route('/billing')
@login_required
def billing():
    return render_template('billing.html', user=current_user, b=True)

@app.route('/virtual_reality')
@login_required
def virtual_reality():
    return render_template('virtual-reality.html', user=current_user, c=True)

@app.route('/tables')
def index():
    if current_user.is_authenticated and current_user.admin:
        profiles = Profile.query.all()
        return render_template('tables.html', profiles=profiles  , user=current_user, activ=True)        
    else : 
        return redirect('/profile')

@app.route('/')
def add():
    if current_user.is_authenticated:
        return redirect('/profile')
    else : 
        return render_template('sign-up.html', ac=True)

@app.route('/profile')
@login_required
def pro():
    return render_template('profile.html', user=current_user, acti=True)


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if current_user.is_authenticated:
        return redirect('/profile')
    else : 
        if request.method == 'POST':
            success()
        return render_template('sign-in.html', user=current_user, pub_key=pub_key, act=True)

@app.route('/add', methods = ['POST'])
def profile():
    if current_user.is_authenticated:
        return redirect('/profile')
    else : 
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        user = Profile.query.filter_by(email=email).first()
        if user:
            return redirect('/dashboard')

        new_user = Profile(email=email, name=name, password=password, admin=False)

        db.session.add(new_user)
        db.session.commit()

        return redirect('/dashboard')




@app.route('/success', methods=['POST'])
def success():
    if current_user.is_authenticated:
        return redirect('/profile')
    else :    
        captcha_response = request.form['g-recaptcha-response']
        if is_human(captcha_response):
            email = request.form.get('email')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False

            user = Profile.query.filter_by(email=email, password=password).first()
            if not user or not (password == user.password) :
                flash('Please check your login details and try again.')
                return redirect('/sign_in') 

            else : 
                login_user(user, remember=remember)
                return redirect('/')


        else:
            flash('failed to submit captcha, please retry')
            return redirect('/sign_in')


@app.route('/delete/<int:id>')
def delet_data(id):
    data = Profile.query.get(id)
    return render_template('delete.html', user=current_user, data=data)


@app.route('/delete/delete_data/<int:id>')
def delet(id):
    data = Profile.query.get(id)
    db.session.delete(data)
    db.session.commit()
    flash('Deleted succesfully !!')
    return redirect ('/profile')

@app.route('/edit/<int:id>')
@login_required
def edit_data(id):
    data = Profile.query.get(id)
    return render_template('image.html', user=current_user, data=data)

@app.route('/edit/edit_data/<int:id>', methods = ['POST'])
@login_required
def edit_data_image(id):
    data = Profile.query.get(id)
    if request.method == 'POST':
        f = request.files['image']
        name = request.form.get('name')
        desc = request.form.get('desc')
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.session.query(Profile).filter_by(id=id).update({"email":data.email, "name" :name, "password":data.password, "image" : f.filename, "desc":desc})
        db.session.commit()

            
        flash('Update succesfully !!')
        return redirect ('/profile')


@app.route('/profile/edit/<int:id>')
@login_required
def edit_profile_data(id):
    data = Profile.query.get(id)
    return render_template('edit_profile.html', user=current_user, data=data)


@app.route('/profile/edit/edit_data/<int:id>', methods = ['POST'])
@login_required
def edit_profle_dataa(id):
    data = Profile.query.get(id)
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        mob = request.form.get("mob")
        location = request.form.get("location")
        info = request.form.get("info")

        db.session.query(Profile).filter_by(id=id).update({"email":email, "name" :name, "mob" : mob, "location":location, "info" : info })
        db.session.commit()

            
        flash('Update succesfully !!')
        return redirect ('/profile')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/sign_in')



if __name__ == "__main__":
    
    app.run(debug = True)
    
