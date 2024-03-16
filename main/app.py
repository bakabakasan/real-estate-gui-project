from flask import Flask, render_template, jsonify, request
from database import load_estate_from_db, create_db_engine, load_estateitem_from_db, add_message_to_db

app = Flask(__name__)

engine = create_db_engine()

@app.route("/") 
def hello_dreamhouse(): 
    try:
        estate = load_estate_from_db(engine)
        return render_template('home.html', estate=estate) 
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@app.route("/api/estate")
def list_estate():
    try:
        estates = load_estate_from_db(engine)
        return jsonify(estate=estates)
    except Exception as e:
        return jsonify(error=str(e)), 500
    
@app.route("/estateitem/<id>")
def show_estate(id):
  estate_item = load_estateitem_from_db(id)
  if not estate_item:
    return "Not Found", 404
  
  return render_template('estatepage.html', 
                         estate=estate_item)

@app.route("/sent-message", methods=['POST'])
def fill_in_the_form():
    try:
        data = request.form
        page_url = request.referrer
        print("Referrer URL:", page_url)  # Добавляем эту строку для отладки
        add_message_to_db(page_url, data)
        return render_template('sent_message.html', message=data)
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@app.route("/contacts") 
def contact_details(): 
  return render_template('contacts.html')

@app.route("/about-us") 
def about_company(): 
  return render_template('aboutus.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)