from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Crime(Base):
    __tablename__ = 'crimes'
    id = Column(Integer, primary_key=True)
    state = Column(Text)
    ctype = Column(Text)
    crime = Column(Text)
    year = Column(Integer)
    count = Column(Integer)

    def __init__(self, state, ctype, crime, year, count):
        self.state = state
        self.ctype = ctype
        self.crime = crime
        self.year = year
        self.count = count

    def __json__(self, request):
        return {
        'id': self.id,
        'state':self.state,
        'ctype':self.ctype,
        'crime':self.crime,
        'year':self.year,
        'count':self.count}
