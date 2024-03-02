from flask import Flask, render_template, jsonify 
from database import load_estate_from_db

app = Flask(__name__)

@app.route("/") 
def hello_dreamhouse(): 
  estate = load_estate_from_db()
  return render_template('home.html', 
                         estate=estate) 

@app.route("/api/estate")
def list_estate():
  return jsonify(estate) 

if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True) 