from app import db

subs = db.Table('subs',
    db.Column('user_id'  , db.ForeignKey('user.id')  , primary_key=True ),
    db.Column('evento_id', db.ForeignKey('evento.id'), primary_key=True )
)
