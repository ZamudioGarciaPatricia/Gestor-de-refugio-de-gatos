
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
import gestor
from passlib.hash import pbkdf2_sha256
from bson.objectid import ObjectId


app = Flask(__name__)
app.secret_key = 'gatitoss'

app.config['SECRET_KEY_TOKENS'] = 'miaus_tokens_rg'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'refugiodegatitosrecupera@gmail.com' 
app.config['MAIL_PASSWORD'] = 'lmbv wquc jiuh stay'
app.config['MAIL_DEFAULT_SENDER'] = 'refugiodegatitosrecupera@gmail.com'


mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY_TOKENS'])

gestor_obj = gestor.GestorTareas("mongodb+srv://ZGpatricia:REFUGIO@clusterpzg.3drzl88.mongodb.net/?appName=ClusterPZG")


@app.route('/')
def home():
    return render_template('pantallainicial.html')

@app.route('/admin')
def admin():
    lista_de_gatos = gestor_obj.obtener_gatos()
    return render_template('admin.html', gatos=lista_de_gatos)


@app.route('/guardar-gato', methods=['POST'])
def guardar_gato():
    datos_nuevo_gato = {
        "nombre": request.form.get('nombre'),
        "raza": request.form.get('raza'),
        "edad": request.form.get('edad'),
        "sexo": request.form.get('sexo'),
        "esterilizado": request.form.get('esterilizado'),
        "estado": request.form.get('estado'),
        "estado_salud": request.form.get('estado_salud'),
        "enfermedades": request.form.get('enfermedades'),
        "es_cronica": request.form.get('es_cronica'),
        "caracter": request.form.get('caracter'),
        "aspecto": request.form.get('aspecto'),
        "trato_cuidador": request.form.get('trato_cuidador'),
        "descripcion": request.form.get('descripcion')
    }
    
    gestor_obj.guardar_gato(datos_nuevo_gato)
    
    flash('¡Gatito registrado exitosamente!')
    
    return redirect(url_for('admin'))

@app.route('/editar/<id_gato>', methods=['GET'])
def editar_gato(id_gato):
    gato_seleccionado = gestor_obj.obtener_gato_por_id(id_gato)
    
    if gato_seleccionado:
        return render_template('editar.html', gato=gato_seleccionado)
    else:
        flash('El gatito no fue encontrado.')
        return redirect(url_for('admin'))


@app.route('/actualizar-gato/<id_gato>', methods=['POST'])
def actualizar_gato_proceso(id_gato):
    datos_modificados = {
        "nombre": request.form.get('nombre'),
        "raza": request.form.get('raza'),
        "edad": request.form.get('edad'),
        "sexo": request.form.get('sexo'),
        "esterilizado": request.form.get('esterilizado'),
        "estado": request.form.get('estado'),
        "estado_salud": request.form.get('estado_salud'),
        "enfermedades": request.form.get('enfermedades'),
        "es_cronica": request.form.get('es_cronica'),
        "caracter": request.form.get('caracter'),
        "aspecto": request.form.get('aspecto'),
        "trato_cuidador": request.form.get('trato_cuidador'),
        "descripcion": request.form.get('descripcion')
    }
    
    gestor_obj.actualizar_gato(id_gato, datos_modificados)
    
    flash('¡La información del gatito se ha actualizado!')
    return redirect(url_for('admin'))

@app.route('/visitante')
def visitante():
    return render_template('visitante.html')


@app.route('/crea')
def crea():
    return render_template('creacuenta.html')


@app.route('/log')
def log():
    return render_template('login.html')


@app.route('/creacuenta', methods=['GET', 'POST'])
def creacuenta():
    if request.method == 'POST':
        u = request.form.get('user')
        n = request.form.get('nombre completo')
        correo = request.form.get('email') 
        s = request.form.get('secreto')
        
        password_encriptada = pbkdf2_sha256.hash(s)

        if gestor_obj.crear_usuario(u, n, correo, password_encriptada):
            flash('Tu cuenta está lista para empezar.')
            return redirect(url_for('log'))
        else:
            flash('Este usuario o correo ya fue registrado.')
            
    return render_template('ash.html')


@app.route('/login', methods=['GET', 'POST'])
def iniciasesion():
    if request.method == 'POST':
        e = request.form.get('user')
        s = request.form.get('secreto') 
        
        user = gestor_obj.obtener_usuario(e)

        if user and pbkdf2_sha256.verify(s, user['secreto']):
            return redirect(url_for('admin')) 
        else:
            flash('Datos incorrectos.')
            
    return render_template('ash.html')


@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    if request.method == 'POST':
        correo = request.form.get('email')
        user = gestor_obj.obtener_usuario_por_correo(correo)
        
        if user:
            token = serializer.dumps(correo, salt='recuperar-password-salt')
            enlace = url_for('restablecer_con_token', token=token, _external=True)
            
            msg = Message('Restablecer Contraseña - Sistema Tareas', recipients=[correo])
            msg.body = f'''Para restablecer tu contraseña, haz clic en el siguiente enlace:
{enlace}

Este enlace expirará en 10 minutos. Si no solicitaste esto, ignora este correo.'''
            
            try:
                mail.send(msg)
                flash('Se ha enviado un enlace seguro a tu correo electrónico.')
                return redirect(url_for('log'))
            except Exception as ex:
                flash('Error al enviar el correo, contacta al administrador.')
                print(f"Error Mail: {ex}")
        else:
            flash('Ese correo electrónico no está registrado.')
            
    return render_template('recuperar_cuenta.html')


@app.route('/restablecer/<token>', methods=['GET', 'POST'])
def restablecer_con_token(token):
    try:
        correo = serializer.loads(token, salt='recuperar-password-salt', max_age=600)
    except SignatureExpired:
        flash('El enlace de recuperación ha expirado.')
        return redirect(url_for('recuperar'))
    except BadTimeSignature:
        flash('El enlace de recuperación es inválido o fue alterado.')
        return redirect(url_for('recuperar'))

    if request.method == 'POST':
        nueva_s = request.form.get('nuevo_secreto')
        nueva_password_encriptada = pbkdf2_sha256.hash(nueva_s)
        
        if gestor_obj.actualizar_contrasena_por_correo(correo, nueva_password_encriptada):
            flash('Tu contraseña ha sido actualizada con éxito.')
            return redirect(url_for('log'))
        else:
            flash('No se pudo actualizar la contraseña.')
            
    return render_template('nueva_contrasena.html', token=token)


if __name__ == '__main__':
    app.run(debug=True)