from flask import Flask, render_template, jsonify, abort 
from database import load_estate_from_db, create_db_engine, load_estates_from_db

app = Flask(__name__)

engine = create_db_engine()

@app.route("/") 
def hello_dreamhouse(): 
  estate = load_estate_from_db(engine)
  return render_template('home.html', estate=estate) 

@app.route("/api/estate")
def list_estate():
  estates = load_estate_from_db(engine)
  return jsonify(estate=estates) 

@app.route("/estateitem")
def show_estates(id):
  estates = load_estates_from_db(id)
  if estates is None:
    abort(404)
  return jsonify(estates)

if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True) 
  