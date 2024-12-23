from flask import Flask, render_template, request,make_response,redirect,session
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,FloatField
from wtforms.validators import DataRequired, NumberRange


app= Flask(__name__)
app.config["SECRET_KEY"]="mysecretkey"

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


@app.route('/grafica')
def grafica():
    if 'imcs' not in session:
        return redirect('/')
        
    from graficar_datos import get_graph_json
    graphJSON = get_graph_json()
    
    # Crear el historial de mediciones para mostrar
    historial = zip(session['alturas'], session['pesos'], session['imcs'])
    return render_template("grafica.html", graphJSON=graphJSON, historial=historial)

@app.route('/', methods=['GET', 'POST'])
def Inicio():
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
    return render_template('inicio.html', form=form, historial=historial)


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















if __name__ == '__main__':
    app.run(debug=True)