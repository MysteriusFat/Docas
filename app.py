# ========= FLASK ========= #
from flask import *
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash

# ======== GOOGLE SHIT ========= #

from google.cloud import bigquery, storage
from datetime import datetime, timedelta
from PIL import Image
import ee

# ========= MATH SHIT IDK ======= #

import numpy as np
import pandas as pd
import geopandas as gpd
import fiona
import matplotlib.pyplot as plt

# ======== JSON AND MORE SHIT ====== #

import os
import re
import json

from NASA_winner import *
from rgb_example import *

# ========= INICIAR OBJETOS =========== #

app   = Flask( __name__ )
db    = SQLAlchemy( app )
login = LoginManager( app )
ee.Initialize()

# ========= API KEY ============ #

file_json = 'TestJS-9381bfacfaba.json'

# ======= CONFIG ========== #

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'dsakjdlajas'

# ============ SEGURIDAD =============== #

@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

ALLOWED_EXTENSION = set(['json', 'shp'])
def allodef_file( filename ):
    return "." in filename and filename.rsplit( '.', 1 )[1] in ALLOWED_EXTENSION

# ====================================== #

subs = db.Table('subs',
                db.Column('user_id'  , db.ForeignKey('user.id')  , primary_key=True ),
                db.Column('evento_id', db.ForeignKey('evento.id'), primary_key=True )
        )

# ====================================== #

class User( db.Model, UserMixin ):
    id          = db.Column( db.Integer, primary_key = True )
    nombre      = db.Column( db.String )
    apellido    = db.Column( db.String )
    email       = db.Column( db.String )
    contrasena  = db.Column( db.String )

    eventos     = db.relationship('Evento' ,backref="user")  # ONE TO ONE
    zonas       = db.relationship('ZonaInteres' ,backref='user')            # ONE TO MANY

class ZonaInteres( db.Model, UserMixin ):
    id      = db.Column( db.Integer, primary_key = True )
    nombre  = db.Column( db.String, unique = True )
    geojson = db.Column( db.String )
    lan     = db.Column( db.Float )
    lng     = db.Column( db.Float )

    paths   = db.relationship('PathFotos', backref='zonainteres')
    owner   = db.Column( db.Integer, db.ForeignKey('user.id'))

class PathFotos( db.Model, UserMixin ):
    id      = db.Column( db.Integer, primary_key = True )
    url_1   = db.Column( db.String )
    url_2   = db.Column( db.String )
    url_3   = db.Column( db.String )

    np_array = db.Column( db.String )

    fecha = db.Column( db.Date )
    lan1  = db.Column( db.Float )
    lng1  = db.Column( db.Float )
    lan2  = db.Column( db.Float )
    lng2  = db.Column( db.Float )
    area  = db.Column( db.Integer )

    estadisticas = db.relationship( 'Estadisticas', backref='pathfotos' )
    owner        = db.Column( db.Integer, db.ForeignKey('zona_interes.id'))

class Estadisticas( db.Model, UserMixin ):
    id = db.Column( db.Integer, primary_key = True )

    area_00  = db.Column( db.Float )
    area_25  = db.Column( db.Float )
    area_50  = db.Column( db.Float )
    area_75  = db.Column( db.Float )
    area_100 = db.Column( db.Float )

    p_05 = db.Column( db.Float )
    p_25 = db.Column( db.Float )
    p_50 = db.Column( db.Float )
    p_75 = db.Column( db.Float )
    p_95 = db.Column( db.Float )

    promedio = db.Column( db.Float )
    des_ests = db.Column( db.Float )
    pro_pix  = db.Column( db.Float )

    histo = db.Column( db.String )

    owner = db.Column( db.Integer, db.ForeignKey('path_fotos.id'))

class Evento( db.Model, UserMixin ):
    id          = db.Column( db.Integer ,primary_key = True )
    nombre      = db.Column( db.String )
    fecha       = db.Column( db.DateTime )
    ubicacion   = db.Column( db.String )
    descripcion = db.Column( db.String )

    organizador   = db.Column( db.Integer ,db.ForeignKey('user.id'))
    participantes = db.relationship('User' ,secondary=subs ,lazy='subquery' ,backref = db.backref('participantes', lazy=True))

admin = Admin( app )

class MyModelView( ModelView ):
    def is_accessible( self ):
        return current_user.is_authenticated

admin.add_view( MyModelView( Estadisticas, db.session ))
admin.add_view( MyModelView( PathFotos, db.session ))
admin.add_view( MyModelView( ZonaInteres, db.session ))
admin.add_view( MyModelView( User, db.session ))
admin.add_view( MyModelView( Evento, db.session ))


def load_dirty_json( dirty_json ):
    regex_replace = [(r"([ \{,:\[])(u)?'([^']+)'", r'\1"\3"'), (r" False([, \}\]])", r' false\1'), (r" True([, \}\]])", r' true\1')]
    for r, s in regex_replace:
        dirty_json = re.sub(r, s, dirty_json)
    clean_json = json.loads(dirty_json)
    return clean_json

@app.route('/ndvi_time_serie', methods=['POST'])
def ndvi_time_serie():

    zone = ZonaInteres.query.get( request.form['id'] )
    data = zone.geojson
    data = load_dirty_json( data )
    geom, x, y = geom_loading( data )

    now       = datetime.now() # current date and time
    month_now = now.strftime("%m")

    lat =  float(request.form['lat'])
    lon =  float(request.form['lon'])

    dates, ndvi_data, parameters = modis_ndvi_time( geom )
    ndvi_data = np.mean(ndvi_data, axis=(0,1))

    return json.dumps({'month': dates,
                       'ndvi': ndvi_data.tolist()})

# =================== DASHBOARD ===================== #

@app.route('/index', methods=['GET', 'POST'])
@login_required
def Dashboard():
    if request.method == 'POST':
        file = request.files['archivo']
        if file and allodef_file( file.filename ):
            data = json.load( file )
            geom, x, y = geom_loading( data )
            new_zone = ZonaInteres(
            nombre  = request.form['nombre'],
            geojson = str( data ),
            lan     = y,
            lng     = x,
            owner   = current_user.id
            )

            db.session.add( new_zone )
            db.session.commit()

            Sentinel( data , request.form['nombre'], new_zone, geom )

            flash('Zona de interes agregada correctamente.', 'success' )

        else:
            flash('La extension del archivo no es valida, porfavor subir archivos GEOJSON o JSON.', 'warning' )

    if request.args.get('cord'):
        current_zone = ZonaInteres.query.get( request.args.get('cord') )
        if current_zone is not None:

            path         = PathFotos.query.filter_by( owner = current_zone.id ).first()
            estadisticas = Estadisticas.query.filter_by( owner = path.id ).first()

            _id   = current_zone.id
            url_1 = path.url_1
            url_2 = path.url_2

            areas     = [ estadisticas.area_00 ,estadisticas.area_25 ,estadisticas.area_50 ,estadisticas.area_75 ,estadisticas.area_100 ]
            percentil = [estadisticas.p_05, estadisticas.p_25 ,estadisticas.p_50 ,estadisticas.p_75 ,estadisticas.p_95]

            coords        = [ [path.lan1, path.lng1 ],[ path.lan2, path.lng2 ]]
            central_point = [ current_zone.lan, current_zone.lng ]
            fecha         = path.fecha
            area_25       = round(estadisticas.area_25, 2)

        else:
            url_1 = ""
            url_2 = ""
            coords = [[12, 12], [21,21]]
            central_point = [ 20, 20 ]
            fecha = ""
            estadisticas = ""
            area_25 = ""
            _id = ""

            areas = []
            percentil = []

    else:
        current_zone = ZonaInteres.query.first()
        if current_zone is not None:
            path = PathFotos.query.filter_by( owner = current_zone.id ).first()
            if path is not None:
                estadisticas = Estadisticas.query.filter_by( owner = path.id ).first()
                url_1 = path.url_1
                url_2 = path.url_2

                coords = [ [path.lan1, path.lng1 ],[ path.lan2, path.lng2 ]]
                central_point = [ current_zone.lan, current_zone.lng ]
                fecha = path.fecha
                area_25 = round(estadisticas.area_25, 2)
                _id = current_zone.id
                areas = [ estadisticas.area_00 ,estadisticas.area_25 ,estadisticas.area_50 ,estadisticas.area_75 ,estadisticas.area_100 ]
                percentil = [estadisticas.p_05, estadisticas.p_25 ,estadisticas.p_50 ,estadisticas.p_75 ,estadisticas.p_95]

            else:
                url_1 = ""
                url_2 = ""
                coords = [[20, 20], [21, 21]]
                central_point = [ 20, 21 ]
                fecha = ""
                estadisticas = ""
                area_25 = ""
                _id = ""

                percentil = []
                areas = []
        else:
            url_1  = ""
            url_2  = ""
            coords = [[20, 20], [21, 21]]
            central_point = [ 20, 21 ]
            fecha = ""
            estadisticas = ""
            area_25 = ""
            _id = ""

            areas = []
            percentil = []


    zonas = ZonaInteres.query.filter_by( owner = current_user.id )
    return render_template( "Dashboard.html",
                            zonas         = zonas,
                            url_1         = url_1,
                            url_2         = url_2,
                            coords        = coords,
                            central_point = central_point,
                            fecha         = fecha,
                            estadisticas  = estadisticas,
                            area_25       = area_25,
                            _id           = _id,
                            areas         = areas,
                            current_user  = current_user,
                            percentil     = percentil
                            )

# =============== GOOGLE EARTH ENGINEL ============== #

def Sentinel( data, name, zone, geom ):

    file_json = 'TestJS-9381bfacfaba.json'
    bucket_name = 'docas'

    predio = 10014
    now    = datetime.now()
    delta  = timedelta( weeks = 6 )
    date_time = now.strftime("%Y-%m-%d")
    past_time = (now-delta).strftime("%Y-%m-%d")

    dates, ndvi_data, parameters = modis_ndvi_time( geom )
    ndvi_data = np.mean( ndvi_data, axis=(0,1) )

    np.save( name ,ndvi_data )
    numpy_save = np.load( name + ".npy" )

    ndvi, now_date, coords, geotrasform, stats = ndvi_sentinel_calculation( geom, past_time, date_time )
    colormap_image( name+"NDIV" , ndvi )

    client = storage.Client.from_service_account_json( file_json )
    bucket = client.get_bucket(bucket_name)
    url_ndvi = upload_ndvi( name+"NDIV" , bucket )


    rgb_data, now_date, coords, parameters = rgb_sentinel( geom, past_time, date_time )
    colormap_rgb( name+"RGB", rgb_data )
    client = storage.Client.from_service_account_json( file_json )
    bucket = client.get_bucket(bucket_name)
    url_rgb = upload_ndvi( name+"RGB" , bucket )



    new_foto = PathFotos(
                            url_1 = url_ndvi,
                            url_2 = url_rgb,
                            fecha = datetime.now(),
                            lan1 = coords[0][0],
                            lng1 = coords[0][1],

                            #np_array = numpy_save,

                            lan2 = coords[1][0],
                            lng2 = coords[1][1],
                            owner = zone.id
                        )

    db.session.add( new_foto )
    db.session.commit()

    new_estadisticas = Estadisticas(
                            area_00  = stats['area_0.00'],
                            area_25  = stats['area_0.25'],
                            area_50  = stats['area_0.50'],
                            area_75  = stats['area_0.75'],
                            area_100 = stats['area_1.00'],
                            p_05 = stats['p_0.05'],
                            p_25 = stats['p_0.25'],
                            p_50 = stats['p_0.50'],
                            p_75 = stats['p_0.75'],
                            p_95 = stats['p_0.95'],
                            promedio = stats['mean'],
                            des_ests = stats['std'] ,
                            pro_pix  = stats['mean/pixel'],
                            owner    = new_foto.id
                        )
    db.session.add( new_estadisticas )
    db.session.commit()

# ================ QUIENES SOMOS ==================== # Contactos y esas weas

@app.route('/quienes-somos')
def QuienesSomos():
    return render_template('QuienesSomos.html')

@app.route('/contacto')
def Contacto():
    return "<h1> Contacto </h1>"

# ===================== LISTA ======================= #

@app.route('/eventos', methods=['GET', 'POST'])
def Lista():
    if request.method == 'POST':
        new_event = Evento(
            nombre      = request.form['nombre'],
            fecha       = datetime.strptime(request.form['fecha'], '%Y-%m-%d'),
            ubicacion   = request.form['ubicacion'],
            descripcion = request.form['descripcion'],
            organizador = current_user.id
        )
        db.session.add( new_event )
        db.session.commit()

    eventos = Evento.query.all()

    return render_template('Lista.html', eventos = eventos )

@app.route('/addPeople', methods=['POST'] )
def AddPeople():
    event = Evento.query.get( request.form['event_id'] )
    user  = User.query.get( request.form['user_id'] )
    print( event )
    print( user )
    try:
        event.participantes.append( user )
        db.session.commit()
        return True
    except:
        return False


# =================================================== #

# ============ LOGIN | LOG OUT | SIG UP ============= #

@app.route('/', methods = ['GET', 'POST'])
def Index():
    if request.method == 'POST':
        user = User.query.filter_by( email = request.form['email'] ).first()

        if user is not None and check_password_hash(user.contrasena, request.form['contrasena']):
            login_user( user )
            return redirect( url_for( 'Dashboard' ))
        else:
            flash("Las credenciales son incorrectas. Revisa e intenta denuevo", 'danger')

    return render_template('Login.html')

@app.route('/sigup', methods= ['GET', 'POST'])
def Registrarse():
    if request.method == 'POST':

        hash_pw = generate_password_hash( request.form['contrasena'], method="sha256")

        New_user = User(
                            nombre     = request.form['nombre'],
                            apellido   = request.form['apellido'],
                            email      = request.form['email'],
                            contrasena = hash_pw
                        )

        db.session.add( New_user )
        db.session.commit()

        flash(" Te haz registrado correctamente.", 'success' )
        return redirect(url_for('Index'))

    return render_template('SipUp.html')

@app.route('/logout')
@login_required
def LogOut():
    logout_user()
    flash('Te desconectasde con exito. ', 'warning')
    return redirect( url_for('Index') )

if __name__ == "__main__":
    db.create_all()
    app.run( debug = True )
