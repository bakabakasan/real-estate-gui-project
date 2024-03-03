from flask import Flask, render_template, jsonify 
from database import load_estate_from_db, create_db_engine

app = Flask(__name__)

config_filename = 'config.json'
engine = create_db_engine(config_filename)

@app.route("/") 
def hello_dreamhouse(): 
  estate = load_estate_from_db(engine)
  return render_template('home.html', estate=estate) 

@app.route("/api/estate")
def list_estate():
  estate = load_estate_from_db(engine)
  return jsonify(estate=estate) 

if __name__ == "__main__":
  app.run(host="127.0.0.1", debug=True) 