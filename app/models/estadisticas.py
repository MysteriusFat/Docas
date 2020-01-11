from app import db
from flask_login import UserMixin

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

def CreateStatistics(area_00,area_25,area_50,area_75,area_100,p_05,p_25,p_50,p_75,p_95,promedio,des_ests,pro_pix, id ):
    new_estadisticas = Estadisticas(
        area_00  = area_00,
        area_25  = area_25,
        area_50  = area_50,
        area_75  = area_75,
        area_100 = area_100,
        p_05 = p_05,
        p_25 = p_25,
        p_50 = p_50,
        p_75 = p_75,
        p_95 = p_95,
        promedio = promedio,
        des_ests = des_ests,
        pro_pix  = pro_pix,
        owner    = id
    )
    db.session.add( new_estadisticas )
    db.session.commit()
