from flask import Flask, render_template, request,make_response,redirect,session
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,FloatField
from wtforms.validators import DataRequired, NumberRange
import webview
from graficar_datos import json_grafica # type: ignore


app= Flask(__name__)
app.config["SECRET_KEY"]="mysecretkey"

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

@app.route('/cerrar-sesion') # TODO: eliminar si no se usa cuando le pongamos la BD
def cerrar_sesion():
    session.clear()  
    return redirect(('/'))





















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













