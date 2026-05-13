from flask import Flask, render_template, request, redirect, url_for, flash
import gestor
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.secret_key = 'gatitolula'

gestor_obj = gestor.GestorTareas("mongodb://127.0.0.1:27017/")

@app.route('/')
def home():
    return render_template('inicio.html')

@app.route('/creacuenta', methods=['GET', 'POST'])
def creacuenta():
    if request.method == 'POST':
        u = request.form.get('user')
        e = request.form.get('nombre completo')
        s = request.form.get('secreto')
        
        password_encriptada = pbkdf2_sha256.hash(s)

        if gestor_obj.crear_usuario(u, e, password_encriptada):
            flash('Tu cuenta esta lista para empezar.')
            return redirect(url_for('login.html'))
        else:
            flash('Este usario ya fue registrado.')
            
    return render_template('crearcuenta.html')

@app.route('/login', methods=['GET', 'POST'])
def iniciasesion():
    if request.method == 'POST':
        e = request.form.get('user')
        s = request.form.get('secreto') 
        
        user = gestor_obj.obtener_usuario(e)

        if user and pbkdf2_sha256.verify(s, user['secreto']):
            return redirect(url_for('tareas'))
        else:
            flash('datos incorrectos.')
            
    return render_template('iniciarsesion.html')

if __name__ == '__main__':
    app.run(debug=True)