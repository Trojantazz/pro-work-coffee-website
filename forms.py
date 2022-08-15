from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, SelectField, BooleanField
from wtforms.validators import DataRequired, url, InputRequired
from flask_ckeditor import CKEditorField


##WTForm
class CafeForm(FlaskForm):
    name = StringField("Cafe name", validators=[DataRequired()])
    map_url = StringField("Cafe location on Google Maps(URL)", validators=[DataRequired(), url(require_tld=True)])
    image_url = StringField("Image of cafe(url)", validators=[DataRequired(), url(require_tld=True)])
    location = StringField("Cafe location", validators=[DataRequired()])
    seats = SelectField("How many people can the cafe accommodate",choices=["1-10", "10-20", "20-30", "30-40", "50+"])
    has_sockets = BooleanField("Cafe has power sockets", validators=[DataRequired()])
    has_toilet = BooleanField("Cafe has toilets", validators=[DataRequired()])
    has_wifi = BooleanField("cafe has Wi-Fi", validators=[DataRequired()])
    can_take_calls = BooleanField("Cafe can take calls", validators=[DataRequired()])
    coffee_price = StringField("Cafe coffee price", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[InputRequired(message="enter a valid Email address, remember to include @ "
                                                                  "sign and a valid smtp server(Yahoo,Gmail etc.", )])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[InputRequired(message="enter a valid Email address, remember to include @ "
                                                                  "sign and a valid smtp server(Yahoo,Gmail etc.", )])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In")


class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")
