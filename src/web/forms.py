from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Length
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class SignupForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Registrarse')

class RecuperarPasswordForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    nueva_password = PasswordField('Nueva Contraseña', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Cambiar Contraseña')

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
    
    anio = SelectField('Año', choices=[], validators=[DataRequired()])
    
    peso = FloatField('Peso (kg)', validators=[
        DataRequired(), 
        NumberRange(min=20, max=300, message="Peso debe estar entre 20 y 300 kg")
    ])
    submit = SubmitField('Registrar Peso')

    def __init__(self, *args, **kwargs):
        super(RegistrarPesoForm, self).__init__(*args, **kwargs)
        año_actual = datetime.now().year
        self.anio.choices = [(str(año), str(año)) for año in range(2000, año_actual + 6)]

class UsuarioForm(FlaskForm):
    dni = StringField('DNI', validators=[DataRequired()])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=50)])
    apellido = StringField('Apellido', validators=[DataRequired(), Length(max=50)])
    altura = FloatField('Altura (m)', validators=[
        DataRequired(), 
        NumberRange(min=0.5, max=2.5)
    ])
    peso_inicial = FloatField('Peso Inicial (kg)', validators=[
        DataRequired(), 
        NumberRange(min=20, max=300)
    ])
    peso_ideal = FloatField('Peso Ideal (kg)', validators=[
        DataRequired(), 
        NumberRange(min=20, max=300)
    ])
    submit = SubmitField('Guardar')
