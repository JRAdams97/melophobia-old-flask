from flask import Flask, render_template
from flask_pymongo import PyMongo

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
app.config["MONGO_URI"] = 'mongodb+srv://admin:T6PsBgmpzdmQNAxX@melophobia-serverless.4jsys.mongodb.net/melophobia'\
                          '?retryWrites=true&w=majority'

mongo = PyMongo(app)


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
