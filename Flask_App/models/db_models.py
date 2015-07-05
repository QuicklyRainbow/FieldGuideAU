__author__ = 'lachlan'

from Flask_App import db

# Create mapping from db objects to named objects for simplicity
Model = db.Model
Column = db.Column
Enum = db.Enum
String = db.String
Integer = db.Integer
DateTime = db.DateTime
Boolean = db.Boolean
Table = db.Table
ForeignKey = db.ForeignKey
Index = db.Index
Metadata = db.MetaData
relationship = db.relationship
Float = db.Float
Text = db.Text


class Request(Model):
    __tablename__ = 'request'

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True)
    time = Column(DateTime)
    person = Column(String)


class Thing(Model):
    __tablename__ = 'thing'

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True)
    name = Column(String)
    image_url = Column(String)
    description = Column(Text)
    description_url = Column(String)
    request_id = Column(Integer, ForeignKey('request.id'))
    request = relationship('Request', backref="things")
