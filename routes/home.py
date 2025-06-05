from flask import Flask, render_template
import os

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))

@app.route("/")
def home():
    return render_template("home.html", title="Home")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)