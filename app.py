from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

#db.init_app(app)

# Routes
@app.route('/')
def home():
    return "Hospital Management System"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Tables created successfully!")
    app.run(debug=True)