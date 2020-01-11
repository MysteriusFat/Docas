from app import db, app
from flask_login import login_required, current_user
from app.models.user import CreateUser, LoginUser
from flask import request, render_template, flash, redirect, url_for

@app.route('/', methods = ['GET', 'POST'])
def Index():
    if request.method == 'POST':
        if LoginUser( request.form['email'], request.form['password'] ):
            flash("Bienvenido {} {}".format(current_user.nombre, current_user.apellido ), 'success')
            return redirect( url_for( 'Dashboard' ))
        else:
            flash("Las credenciales son incorrectas. Revisa e intenta denuevo", 'danger')
    return render_template('login.html')

@app.route('/sigup', methods= ['POST'])
def Registrarse():
    CreateUser( request.form['nombre'], request.form['apellido'], request.form['email'],  request.form['contrasena'] )
    flash(" Te haz registrado correctamente.", 'success')
    return redirect(url_for('Index'))

@app.route('/logout')
@login_required
def LogOut():
    logout_user()
    flash('Te desconectasde con exito. ', 'warning')
    return redirect( url_for('Index') )
