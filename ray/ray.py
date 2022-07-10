"""
# ray.py
#
# Directive:
#   Provide interface for testing concepts
#   Template for database implementation
#   Probability of syllable progression
#
#
# Notes:
#   May be better if developed in a oop linked node format.
#   Extending previous order objects will maintain some consistancy
#   Updates to calculations need proper flow because of child dependencies
"""
# Shane_Hazelquist #Date: Monday, 6/20/2022
# Imports:
from os import environ
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Enum,
    ForeignKey,
    create_engine,
    UniqueConstraint,
    and_,
)
from sqlalchemy.orm import relationship, Session, backref
from sqlalchemy.ext.declarative import declarative_base

dburl=environ.get('DB_URI', "sqlite:///ray.db")
temp_path = '../temp/'# not used directly but by dependent modules
if 'jp' in dburl:
    temp_path = '../archive/temp/'# not used directly but by dependent modules

Base = declarative_base()
engine = None
session = None


def start_session():
    """initial setup with base data"""
    global engine
    global session
    print("creating engine for {}".format(dburl))
    engine = create_engine(dburl)
    print("opening session")
    session = Session(engine)


start_session()

stale_instance = True
instance_sum = 0
stale_following = True  # probably unneeded


class instance(Base):
    """
    syllabary

    __init__(sylb, frequency=0)
    Maintains syllable information for calculation and reference

    text
    freq
    prob
    """

    __tablename__ = "instance"
    id = Column(Integer, primary_key=True, unique=True)
    text = Column(String, unique=True)
    freq = Column(Integer)
    #prob = Column(Float(unsigned=True))

    def __init__(self, text, freq):
        """ """
        global stale_instance
        stale_instance = True
        self.text = text
        self.freq = freq

    def update_freq(self, value):
        """ """
        global stale_instance
        stale_instance = True
        self.freq = value

    def probability(self):
        """ """
        global stale_instance, instance_sum
        if stale_instance:
            instance_sum = sum([i[0] for i in session.query(instance.freq).all()])
            stale_instance = False

        self.prob = self.freq / instance_sum
        return self.prob

    def __repr__(self):
        """ """
        return '<{} id={} text="{}" freq={}, prob={}>'.format(
            type(self), self.id, self.text, self.freq, self.probability()
        )

class following(Base):
    """
    syll_relation

    __init__(parent, child, frequency)

    Given an ancester, keep track of likelyhood of following syllables
    column view of matrix
    needs special terminal cases
    Intended for use in word progression
    """

    __tablename__ = "following"
    id = Column(Integer, primary_key=True, unique=True)
    parent_id = Column(Integer, ForeignKey('instance.id'))
    parent = relationship("instance", primaryjoin='instance.id==following.parent_id')
    text_id = Column(Integer, ForeignKey('instance.id'))
    text = relationship("instance", primaryjoin='instance.id==following.text_id')
    freq = Column(Integer)
    # prob=Column(Float) # probably unneeded

    def __init__(self, parent, text, frequency):
        """ """
        self.parent_id = parent
        self.text_id = text
        self.freq = frequency

    def update_freq(self, value):
        """ """
        global stale_following
        stale_following = True
        self.freq = value

    def probability(self):
        """ """
        self.prob= self.freq / sum([child.freq for child in session.query(following).filter(following.parent_id==self.parent_id).all()])
        return self.prob

    def total_probability(self):
        """ """
        return self.prob*self.parent.probability()

    def __repr__(self):
        """ """
        return "<{} id={} parent_id={} child_id={} freq={}>".format(
            type(self), self.id, self.parent_id, self.text_id, self.freq
        )

class model_source():
    """
    A collection of locations or addresses from where information was collected
    """
    id=Column(Integer, primary_key=True, unique=True)
    source = Column(String)
    tag = Column(String)


class folowing_plus(following):
    """
    higher_relation

    __init__(parent_table, parent, child, frequency)

    Given an ancester, keep track of likelyhood of following syllables
    Using parent_table as a reference, we can direct parent queries to higher order
    """

def main():
    global session
    setup=False
    print('instances {}, following {}'.format(session.query(instance).count(),session.query(following).count()))
    if setup:
        print("creating engine")
        engine = create_engine(dburl)
        print("dropping existing")
        Base.metadata.drop_all(engine)
        print("creating all schemea")
        Base.metadata.create_all(engine)
        print("opening session")
        session = Session(engine)


if __name__=='__main__':
    main()
