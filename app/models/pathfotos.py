from app import db
from flask_login import UserMixin

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

def CreatePathFoto( url_ndvi, url_rgb, lan1, lng1, lan2, lng2, id ):
    new_foto = PathFotos(
        url_1 = url_ndvi,
        url_2 = url_rgb,
        fecha = datetime.now(),
        lan1 = coords[0][0],
        lng1 = coords[0][1],
        #np_array = numpy_save,
        lan2 = coords[1][0],
        lng2 = coords[1][1],
        owner = id
    )
    db.session.add( new_foto )
    db.session.commit()
    return new_foto.id
