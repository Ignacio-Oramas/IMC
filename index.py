# index.py
from flask import Flask, render_template, request, make_response, redirect, session, flash, g
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField
from wtforms.validators import DataRequired, NumberRange
import webview
from graficar_datos import json_grafica # type: ignore
from database import get_db, init_db  # Importa init_db
import sqlite3

app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecretkey"

# Inicializar la base de datos al iniciar la aplicación
init_db()

#* Clase formulario que se usa en el inicio
class IMCForm(FlaskForm):
    altura = FloatField('Altura (metros)', validators=[
        DataRequired(), 
        NumberRange(min=0.5, max=2.5, message="Altura debe estar entre 0.5 y 2.5 metros")
    ])
    peso = FloatField('Peso (kg)', validators=[
        DataRequired(),
        NumberRange(min=20, max=300, message="Peso debe estar entre 20 y 300 kg")
    ])
    submit = SubmitField('Calcular IMC')

#*Pagina de inicio
@app.route('/')
def Inicio():
    return render_template('inicio.html')

#*Caculadora
@app.route('/calculadoraimc', methods=['GET', 'POST'])
def CalculadoraIMC():
    form = IMCForm()
    if form.validate_on_submit():
        altura = form.altura.data
        peso = form.peso.data
        imc = peso / (altura ** 2)
        
        # Inicializar o actualizar las listas en la sesión
        if 'alturas' not in session:
            session['alturas'] = []
            session['pesos'] = []
            session['imcs'] = []
        
        # Agregar nuevas mediciones
        session['alturas'] = session['alturas'] + [altura]
        session['pesos'] = session['pesos'] + [peso]
        session['imcs'] = session['imcs'] + [imc]
        
        # Guardar los cambios en la sesión
        session.modified = True
        
        return redirect('/grafica')
    historial = None
    if 'imcs' in session:
        historial = zip(session['alturas'], session['pesos'], session['imcs'])
    return render_template('calculadoraIMC.html', form=form, historial=historial)

#* GRAFICA
@app.route('/grafica')
def grafica():
    if 'imcs' not in session:
        return redirect('/')
    graphJSON = json_grafica()
    historial = zip(session['alturas'], session['pesos'], session['imcs'])
    return render_template("grafica.html", graphJSON=graphJSON, historial=historial)

#* reset valores de la sesion
@app.route('/reset')
def reset_mediciones():
    session.pop('alturas', None)
    session.pop('pesos', None)
    session.pop('imcs', None)
    return redirect('/')

@app.route('/cerrar-sesion')
def cerrar_sesion():
    session.clear()  
    return redirect('/')

#* Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and user['password'] == password:
            session['user_id'] = user['id']
            flash('Login successful!', 'success')
            return redirect('/')
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

#* Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        try:
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            db.commit()
            flash('Signup successful! Please login.', 'success')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('Username already exists', 'error')
    return render_template('signup.html')

def Ventana(entrada):
    if (entrada==True):
        webview.create_window(
                "Mi Aplicación Flask",  # Título de la ventana
                "http://127.0.0.1:5000",  # URL de Flask
                width=800,  # Ancho de la ventana
                height=600,  # Alto de la ventana
            )
        webview.start()  # Iniciar la ventana

if __name__ == '__main__':
    app.run(debug=True)
    Ventana(False)