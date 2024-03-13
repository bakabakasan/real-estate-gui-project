from flask import Flask, render_template, jsonify
from database import load_estate_from_db, create_db_engine, load_estateitem_from_db

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

@app.route("/estateitem/<id>")
def show_estate(id):
  estate_item = load_estateitem_from_db(id)
  if not estate_item:
    return "Not Found", 404
  
  return render_template('estatepage.html', estate=estate_item)

@app.route("/contacts") 
def contact_details(): 
  return render_template('contacts.html')

@app.route("/about-us") 
def about_company(): 
  return render_template('aboutus.html')

if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True) 
  