from app import db, app
from app.models.eventos import CreateEvent

@app.route('/eventos', methods=['GET', 'POST'])
def Lista():
    if request.method == 'POST':
        CreateEvent( request.form['nombre'], request.form['ubicacion'], equest.form['descripcion'] )

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
