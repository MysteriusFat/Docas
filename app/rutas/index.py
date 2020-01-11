from app import app
from flask_login import login_required, current_user
from app.models.zonainteres import CreateZone
from app.models.user import IndexData
from app.models.zonainteres import ZonaInteres

from flask import request, render_template, flash

@app.route('/index', methods=['GET', 'POST'])
@login_required
def Dashboard():
    if request.method == 'POST':
        CreateZone( request.form['nombre'], request.files['archivo'] )
        flash('Zona de interes agregada correctamente.', 'success' )
    
    if request.args.get('cord'):
        url_1, url_2, coords, central_point, fecha, estadisticas, area_25, _id, areas, percentil = IndexData( request.args.get('cord') )
    else:
        url_1, url_2, coords, central_point, fecha, estadisticas, area_25, _id, areas, percentil = IndexData( 0 )

    zonas = ZonaInteres.query.filter_by( owner = current_user.id )
    return render_template( "dashboard.html",
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
