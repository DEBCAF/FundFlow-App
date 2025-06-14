from flask import Flask, render_template, url_for
import os
from forms.RegistrationForm import RegistrationForm
from forms.LoginForm import LoginForm

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))

app.config['SECRET_KEY'] = '5773526bb0b13ce0c676dfde280ba345'

@app.route("/home")
@app.route("/")
def home():
    return render_template("home.html", title="FundFlow")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template("login.html", title="Login", form=form)

if __name__ == "__main__":
    app.run(debug=True)