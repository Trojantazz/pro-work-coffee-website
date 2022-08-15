from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import LoginForm, RegisterForm, CafeForm
from flask_gravatar import Gravatar
import os

# -------------- Initialize Application --------------- #
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('KREFJEZIVOT')
ckeditor = CKEditor(app)
Bootstrap(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False,
                    base_url=None)

# ----------------- Connect Database ------------------ #
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL1', 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# -------------- LOAD USER FUNCTION -------------- #
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------- CONFIGURE CAFE TABLE -------------- #
class Cafe(db.Model):
    __tablename__ = 'cafe'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    users = relationship("User")

# -------------- CONFIGURE USER TABLE -------------- #
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    cafe_id = db.Column(db.Integer, db.ForeignKey('cafe.id'))


db.create_all()

# -------------- ALLOW ADMIN FUNCTIONS -------------- #
def admin_only(f):
    @wraps(f)
    def admin_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return admin_function


# -------------- RENDERS HOME PAGE -------------- #
@app.route('/')
def home():
    current_year = datetime.now().year
    cafes = Cafe.query.all()
    return render_template("index.html", year=current_year, all_cafes=cafes, current_user=current_user)


# -------------- RENDERS REGISTRATION FORM/PAGE -------------- #
@app.route('/register', methods=["GET", "POST"])
def register_user():
    current_year = datetime.now().year
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())
            # user already exists
            flash("You've already signed up with that email, log in instead")
            return redirect(url_for('login'))
        # password encryption
        hashed_and_salted_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)

        new_user = User(email=form.email.data,
                        username=form.username.data,
                        password=hashed_and_salted_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("Thank you for joining our growing community!")
        return redirect(url_for('show_cafes'))
    return render_template("register.html", form=form, current_user=current_user, year=current_year)


# -------------- RENDERS LOGIN FORM/PAGE -------------- #
@app.route('/login', methods=["GET", "POST"])
def login():
    current_year = datetime.now().year
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data

        user = User.query.filter_by(email=form.email.data).first()
        # Email verification message
        if not user:
            flash("That email does not exist, please try again.")
        elif not check_password_hash(user.password, password):
            flash("Password incorrect,please try again.")
        else:
            login_user(user)
            return redirect(url_for('show_cafes'))
    return render_template("login.html", form=form, current_user=current_user, year=current_year)


# -------------- RENDERS ADD CAFE FORM PAGE -------------- #
@app.route('/add', methods=["GET", "POST"])
@login_required
def add_cafe():
    current_year = datetime.now().year
    form = CafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe(name=form.name.data,
                        map_url=form.map_url.data,
                        image_url=form.image_url.data,
                        location=form.location.data,
                        seats=form.seats.data,
                        has_sockets=form.has_sockets.data,
                        has_toilets=form.has_toilet.data,
                        has_wifi=form.has_wifi.data,
                        can_take_calls=form.can_take_calls.data,
                        coffee_price=form.coffee_price.data)
        db.session.add(new_cafe)
        db.session.commit()

        return redirect(url_for("cafes"))
    return render_template("add_cafe.html", form=form, year=current_year)


# -------------- RENDERS CAFE FORM PAGE -------------- #
@app.route('/cafes')
def show_cafes():
    current_year = datetime.now().year
    all_cafes = Cafe.query.order_by(Cafe.id).all()
    for i in range(len(all_cafes)):
        all_cafes[i].ranking = len(all_cafes) - i
    db.session.commit()

    counter = 0
    cafes_to_append = []
    all_cafes_three_list = []
    # create lists of three cafes inside a big list:
    for _ in all_cafes:
        cafes_to_append.append(all_cafes[counter])
        counter += 1
        if len(cafes_to_append) % 3 != 0:
            continue
        else:
            all_cafes_three_list.append(cafes_to_append)
            cafes_to_append = []
    # if there are leftovers in cafes_to_append, add them to the list as well:
    if len(cafes_to_append) > 0:
        all_cafes_three_list.append(cafes_to_append)

    return render_template("cafes.html", all_cafes=all_cafes_three_list, current_user=current_user, year=current_year)


# -------------- LOGOUT BUTTON FUNCTION -------------- #
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# -------------- DELETE BUTTON FUNCTION -------------- #
@app.route('/delete')
@login_required
def delete():
    cafe_id = request.args.get('id')
    cafe = Cafe.query.get(cafe_id)
    db.session.delete(cafe)
    db.commit()
    return redirect(url_for('cafes'))


if __name__ == "__main__":
    app.run()
