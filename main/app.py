from flask import Flask, render_template, jsonify, request, redirect
from database import load_estate_from_db, create_db_engine, load_estateitem_from_db, add_message_to_db, register_form, authenticate_user
from sqlalchemy.exc import SQLAlchemyError

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
    return render_template('estatepage.html', estate=estate_item)

@app.route("/sent-message", methods=['POST'])
def fill_in_the_form():
    try:
        data = request.form
        page_url = request.referrer
        print("Referrer URL:", page_url)  # Для отладки: проверяем URL-адрес предыдущей страницы
        print("Form Data:", data)  # Для отладки: проверяем данные формы
        add_message_to_db(page_url, data)
        return render_template('sent_message.html', data=data)
    except SQLAlchemyError as e:
        return render_template('error.html', error=str(e)), 500

@app.route("/contacts") 
def contact_details(): 
    return render_template('contacts.html')

@app.route("/about-us") 
def about_company(): 
    return render_template('aboutus.html')

@app.route("/register", methods=['GET', 'POST']) 
def register(): 
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not name or not email or not password:
                return render_template('error.html', error='Please fill out all fields'), 400
            
            register_form(name, email, password)
        
        return render_template('register.html') 
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@app.route("/login", methods=['GET', 'POST']) 
def login():
    try:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            # Проверяем аутентификацию пользователя
            if authenticate_user(email, password):
                # Если аутентификация успешна, устанавливаем сессию для пользователя
                return redirect('/')
            else:
                # Если аутентификация не удалась, возвращаем сообщение об ошибке на страницу входа
                return render_template('login.html', error='Invalid email or password')

        return render_template('login.html')
    except Exception as e:
        return render_template('error.html', error=str(e)), 500  

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
