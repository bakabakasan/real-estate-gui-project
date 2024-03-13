from flask import Flask, render_template, jsonify, request
from database import load_estate_from_db, create_db_engine, load_estateitem_from_db

app = Flask(__name__)

engine = create_db_engine()

@app.route("/") 
def hello_dreamhouse(): 
  estate = load_estate_from_db(engine)
  return render_template('home.html', 
                         estate=estate) 

@app.route("/api/estate")
def list_estate():
  estates = load_estate_from_db(engine)
  return jsonify(estate=estates) 

@app.route("/estate-item/<id>")
def show_estate(id):
  estate_item = load_estateitem_from_db(id)
  if not estate_item:
    return "Not Found", 404
  
  return render_template('estatepage.html', 
                         estate=estate_item)
  
@app.route("/sent-message", methods=['post'])
def fill_in_the_form():
  data = request.form
  #store this in DB
  #display an aknowlegment
  return render_template('sent_message.html',
                         message=data) 

@app.route("/contacts") 
def contact_details(): 
  return render_template('contacts.html')

@app.route("/about-us") 
def about_company(): 
  return render_template('aboutus.html')

if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True) 
  