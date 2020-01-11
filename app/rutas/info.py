from app import app, db
from flask import render_template

@app.route('/quienes-somos')
def QuienesSomos():
    return render_template('QuienesSomos.html')

@app.route('/contacto')
def Contacto():
    return "<h1> Contacto </h1>"
