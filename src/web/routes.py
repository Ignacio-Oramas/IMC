from flask import render_template, request, flash, redirect, session, url_for
from .forms import (LoginForm, SignupForm, RecuperarPasswordForm, 
                    AccesoUsuarioForm, EditarAlturaForm, RegistrarPesoForm, UsuarioForm)
from ..core.security import hashear_password, verificar_password
from ..core.viz import generar_json_evolucion_imc

def register_routes(app, repo):
    
    @app.route('/')
    def inicio():
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = repo.obtener_entrenador_por_username(form.username.data)
            if user and verificar_password(user['password'], form.password.data):
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash('Inicio de sesión exitoso', 'success')
                return redirect(url_for('dashboard_entrenador'))
            flash('Usuario o contraseña incorrectos', 'error')
        return render_template('login.html', form=form)

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        form = SignupForm()
        if form.validate_on_submit():
            hash_pwd = hashear_password(form.password.data)
            try:
                repo.crear_entrenador(form.username.data, hash_pwd)
                flash('Registro exitoso. Por favor, inicia sesión.', 'success')
                return redirect(url_for('login'))
            except Exception:
                flash('El nombre de usuario ya existe o hubo un error', 'error')
        return render_template('signup.html', form=form)

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Sesión cerrada correctamente', 'success')
        return redirect(url_for('login'))

    @app.route('/dashboard_entrenador', methods=['GET', 'POST'])
    def dashboard_entrenador():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        form = AccesoUsuarioForm()
        usuarios = repo.obtener_usuarios_entrenador(session['user_id'])
        
        if form.validate_on_submit():
            usuario = repo.obtener_usuario_por_dni(form.dni.data)
            if usuario:
                return redirect(url_for('dashboard_usuario', dni=usuario['dni']))
            flash('Usuario no encontrado', 'error')
        
        return render_template('dashboard_entrenador.html', form=form, usuarios=usuarios)

    @app.route('/crear_usuario', methods=['GET', 'POST'])
    def crear_usuario_route():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        form = UsuarioForm()
        if form.validate_on_submit():
            if repo.obtener_usuario_por_dni(form.dni.data):
                flash('Error: El DNI ya está registrado.', 'error')
            else:
                repo.crear_usuario({
                    'dni': form.dni.data,
                    'nombre': form.nombre.data,
                    'apellido': form.apellido.data,
                    'altura': form.altura.data,
                    'peso_inicial': form.peso_inicial.data,
                    'peso_ideal': form.peso_ideal.data,
                    'entrenador_id': session['user_id']
                })
                flash('Usuario creado correctamente', 'success')
                return redirect(url_for('dashboard_entrenador'))
        return render_template('crear_usuario.html', form=form)

    @app.route('/dashboard_usuario/<dni>')
    def dashboard_usuario(dni):
        usuario = repo.obtener_usuario_por_dni(dni)
        if not usuario:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('dashboard_entrenador'))
        
        historial = repo.obtener_historial_pesos(usuario['id'])
        return render_template('dashboard_usuario.html', 
                             usuario=usuario, 
                             altura_form=EditarAlturaForm(),
                             peso_form=RegistrarPesoForm(),
                             historial=historial)

    @app.route('/grafica_usuario/<dni>')
    def grafica_usuario(dni):
        usuario = repo.obtener_usuario_por_dni(dni)
        if not usuario:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('dashboard_entrenador'))
        
        anio_inicio = request.args.get('anio_inicio')
        anio_fin = request.args.get('anio_fin')
        
        registros = repo.obtener_historial_pesos(usuario['id'], anio_inicio, anio_fin)
        pesos_map = {f"{r['anio']}-{r['mes']}": r['peso'] for r in registros}
        
        graphJSON = generar_json_evolucion_imc(usuario['altura'], pesos_map)
        if not graphJSON:
            flash('No hay datos en el rango seleccionado', 'warning')
            
        return render_template('grafica.html', graphJSON=graphJSON, dni=dni, 
                             anio_inicio=anio_inicio, anio_fin=anio_fin)

    @app.route('/editar_usuario/<int:usuario_id>', methods=['GET', 'POST'])
    def editar_usuario_route(usuario_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        usuario = repo.obtener_usuario_por_id(usuario_id)
        if not usuario:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('dashboard_entrenador'))
        
        form = UsuarioForm(obj=usuario)
        if form.validate_on_submit():
            repo.actualizar_usuario(usuario_id, {
                'nombre': form.nombre.data,
                'apellido': form.apellido.data,
                'altura': form.altura.data,
                'peso_inicial': form.peso_inicial.data,
                'peso_ideal': form.peso_ideal.data
            })
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('dashboard_entrenador'))
        return render_template('editar_usuario.html', form=form, usuario=usuario)

    @app.route('/eliminar_usuario/<int:usuario_id>')
    def eliminar_usuario_route(usuario_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        repo.eliminar_usuario(usuario_id)
        flash('Usuario eliminado correctamente', 'success')
        return redirect(url_for('dashboard_entrenador'))

    @app.route('/actualizar_altura/<dni>', methods=['POST'])
    def actualizar_altura_route(dni):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        usuario = repo.obtener_usuario_por_dni(dni)
        if not usuario:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('dashboard_entrenador'))
        
        form = EditarAlturaForm()
        if form.validate_on_submit():
            repo.actualizar_altura(usuario['id'], form.nueva_altura.data)
            flash('Altura actualizada correctamente', 'success')
        
        return redirect(url_for('dashboard_usuario', dni=dni))

    @app.route('/registrar_peso/<dni>', methods=['POST'])
    def registrar_peso_route(dni):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        usuario = repo.obtener_usuario_por_dni(dni)
        if not usuario:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('dashboard_entrenador'))
        
        form = RegistrarPesoForm()
        if form.validate_on_submit():
            repo.registrar_peso(
                usuario['id'],
                form.mes.data,
                form.anio.data,
                form.peso.data
            )
            flash('Peso registrado correctamente', 'success')
        
        return redirect(url_for('dashboard_usuario', dni=dni))

    @app.route('/eliminar_peso/<int:peso_id>', methods=['POST'])
    def eliminar_peso(peso_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        repo.eliminar_peso(peso_id)
        flash('Registro de peso eliminado correctamente', 'success')
        return redirect(request.referrer)
