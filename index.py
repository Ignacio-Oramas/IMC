from flask import Flask, render_template, request, flash, redirect, session
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, NumberRange
from database import *
from graficar_datos import json_grafica
from datetime import datetime  # Importa datetime para obtener el año actual

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

# Forms
class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class SignupForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Registrarse')

class AccesoUsuarioForm(FlaskForm):
    dni = StringField('DNI del Usuario', validators=[DataRequired()])
    submit = SubmitField('Acceder')

class EditarAlturaForm(FlaskForm):
    nueva_altura = FloatField('Nueva Altura (m)', validators=[
        DataRequired(), 
        NumberRange(min=0.5, max=2.5, message="Altura debe estar entre 0.5 y 2.5 metros")
    ])
    submit = SubmitField('Actualizar Altura')

class RegistrarPesoForm(FlaskForm):
    mes = SelectField('Mes', choices=[
        ('Enero', 'Enero'), ('Febrero', 'Febrero'), ('Marzo', 'Marzo'),
        ('Abril', 'Abril'), ('Mayo', 'Mayo'), ('Junio', 'Junio'),
        ('Julio', 'Julio'), ('Agosto', 'Agosto'), ('Septiembre', 'Septiembre'),
        ('Octubre', 'Octubre'), ('Noviembre', 'Noviembre'), ('Diciembre', 'Diciembre')
    ], validators=[DataRequired()])
    
    # Generar opciones de años dinámicamente
    anio = SelectField('Año', choices=[], validators=[DataRequired()])
    
    peso = FloatField('Peso (kg)', validators=[
        DataRequired(), 
        NumberRange(min=20, max=300, message="Peso debe estar entre 20 y 300 kg")
    ])
    submit = SubmitField('Registrar Peso')

    def __init__(self, *args, **kwargs):
        super(RegistrarPesoForm, self).__init__(*args, **kwargs)
        # Generar una lista de años desde 2000 hasta el año actual + 5
        año_actual = datetime.now().year
        self.anio.choices = [(str(año), str(año)) for año in range(2000, año_actual + 6)]

@app.route('/editar_usuario/<int:usuario_id>', methods=['GET', 'POST'])
def editar_usuario_route(usuario_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    # Obtener el usuario por su ID
    usuario = obtener_usuario_por_id(usuario_id)
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect('/dashboard_entrenador')
    
    form = EditarUsuarioForm(obj=usuario)
    if form.validate_on_submit():
        actualizar_usuario(
            usuario_id=usuario_id,
            nombre=form.nombre.data,
            apellido=form.apellido.data,
            altura=form.altura.data,
            peso_inicial=form.peso_inicial.data,
            peso_ideal=form.peso_ideal.data
        )
        flash('Usuario actualizado correctamente', 'success')
        return redirect('/dashboard_entrenador')
    
    return render_template('editar_usuario.html', form=form, usuario=usuario)

# Rutas de Autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        db = get_db()
        user = db.execute('SELECT * FROM Entrenador WHERE username = ?', (username,)).fetchone()
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Inicio de sesión exitoso', 'success')
            return redirect('/dashboard_entrenador')
        flash('Usuario o contraseña incorrectos', 'error')
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        db = get_db()
        try:
            db.execute('INSERT INTO Entrenador (username, password) VALUES (?, ?)', (username, password))
            db.commit()
            flash('Registro exitoso. Por favor, inicia sesión.', 'success')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('El nombre de usuario ya existe', 'error')
    return render_template('signup.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'success')
    return redirect('/login')

# Rutas Entrenador
@app.route('/dashboard_entrenador', methods=['GET', 'POST'])
def dashboard_entrenador():
    if 'user_id' not in session:
        return redirect('/login')
    
    form = AccesoUsuarioForm()
    usuarios = obtener_usuarios_entrenador(session['user_id'])
    
    if form.validate_on_submit():
        usuario = obtener_usuario_por_dni(form.dni.data)
        if usuario:
            return redirect(f'/dashboard_usuario/{usuario["dni"]}')
        flash('Usuario no encontrado', 'error')
    
    return render_template('dashboard_entrenador.html', form=form, usuarios=usuarios)

# Rutas Usuario
@app.route('/dashboard_usuario/<dni>')
def dashboard_usuario(dni):
    usuario = obtener_usuario_por_dni(dni)
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect('/dashboard_entrenador')
    
    altura_form = EditarAlturaForm()
    peso_form = RegistrarPesoForm()
    historial = obtener_historial_pesos(usuario['id'])
    
    return render_template('dashboard_usuario.html',
                         usuario=usuario,
                         altura_form=altura_form,
                         peso_form=peso_form,
                         historial=historial)

@app.route('/actualizar_altura/<dni>', methods=['POST'])
def actualizar_altura_route(dni):
    if 'user_id' not in session:
        return redirect('/login')
    
    usuario = obtener_usuario_por_dni(dni)
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect('/dashboard_entrenador')
    
    form = EditarAlturaForm()
    if form.validate_on_submit():
        actualizar_altura(
            usuario_id=usuario['id'],      # ID del usuario
            nueva_altura=form.nueva_altura.data  # Nueva altura
        )
        flash('Altura actualizada correctamente', 'success')
    
    return redirect(f'/dashboard_usuario/{dni}')

@app.route('/registrar_peso/<dni>', methods=['POST'])
def registrar_peso_route(dni):
    if 'user_id' not in session:
        return redirect('/login')
    
    usuario = obtener_usuario_por_dni(dni)
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect('/dashboard_entrenador')
    
    form = RegistrarPesoForm()
    if form.validate_on_submit():
        registrar_peso(
            usuario_id=usuario['id'],  # ID del usuario
            mes=form.mes.data,         # Mes seleccionado
            anio=form.anio.data,       # Año seleccionado
            peso=form.peso.data        # Peso registrado
        )
        flash('Peso registrado correctamente', 'success')
    
    return redirect(f'/dashboard_usuario/{dni}')

@app.route('/grafica_usuario/<dni>')
def grafica_usuario(dni):
    usuario = obtener_usuario_por_dni(dni)
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect('/dashboard_entrenador')
    
    historial = obtener_historial_pesos(usuario['id'])
    
    # Preparar datos para la gráfica
    pesos = {f"{anio}-{mes}": peso for mes, anio, peso in historial}  # Usar mes y año como clave
    graphJSON = json_grafica(usuario['altura'], pesos)
    
    return render_template('grafica.html', graphJSON=graphJSON, dni=usuario['dni'])

# Nuevos Forms
class CrearUsuarioForm(FlaskForm):
    dni = StringField('DNI', validators=[DataRequired()])
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    altura = FloatField('Altura (m)', validators=[
        DataRequired(), 
        NumberRange(min=0.5, max=2.5, message="Altura debe estar entre 0.5 y 2.5 metros")
    ])
    peso_inicial = FloatField('Peso Inicial (kg)', validators=[
        DataRequired(), 
        NumberRange(min=20, max=300, message="Peso debe estar entre 20 y 300 kg")
    ])
    peso_ideal = FloatField('Peso Ideal (kg)', validators=[
        DataRequired(), 
        NumberRange(min=20, max=300, message="Peso debe estar entre 20 y 300 kg")
    ])
    submit = SubmitField('Crear Usuario')

class EditarUsuarioForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    altura = FloatField('Altura (m)', validators=[
        DataRequired(), 
        NumberRange(min=0.5, max=2.5, message="Altura debe estar entre 0.5 y 2.5 metros")
    ])
    peso_inicial = FloatField('Peso Inicial (kg)', validators=[
        DataRequired(), 
        NumberRange(min=20, max=300, message="Peso debe estar entre 20 y 300 kg")
    ])
    peso_ideal = FloatField('Peso Ideal (kg)', validators=[
        DataRequired(), 
        NumberRange(min=20, max=300, message="Peso debe estar entre 20 y 300 kg")
    ])
    submit = SubmitField('Actualizar Usuario')

# Nueva función en database.py
def crear_usuario(dni, nombre, apellido, altura, peso_inicial, peso_ideal, entrenador_id):
    conn = get_db()
    conn.execute(
        'INSERT INTO Usuarios (dni, nombre, apellido, altura, peso_inicial, peso_ideal, entrenador_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (dni, nombre, apellido, altura, peso_inicial, peso_ideal, entrenador_id)
    )
    conn.commit()
    conn.close()

def eliminar_usuario(usuario_id):
    conn = get_db()
    conn.execute('DELETE FROM Usuarios WHERE id = ?', (usuario_id,))
    conn.commit()
    conn.close()

# Nuevas rutas en index.py
@app.route('/crear_usuario', methods=['GET', 'POST'])
def crear_usuario_route():
    if 'user_id' not in session:
        return redirect('/login')
    
    form = CrearUsuarioForm()
    if form.validate_on_submit():
        crear_usuario(
            dni=form.dni.data,
            nombre=form.nombre.data,
            apellido=form.apellido.data,
            altura=form.altura.data,
            peso_inicial=form.peso_inicial.data,
            peso_ideal=form.peso_ideal.data,
            entrenador_id=session['user_id']
        )
        flash('Usuario creado correctamente', 'success')
        return redirect('/dashboard_entrenador')
    
    return render_template('crear_usuario.html', form=form)

@app.route('/eliminar_usuario/<int:usuario_id>')
def eliminar_usuario_route(usuario_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    eliminar_usuario(usuario_id)
    flash('Usuario eliminado correctamente', 'success')
    return redirect('/dashboard_entrenador')

# Ruta de Inicio
@app.route('/')
def inicio():
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)