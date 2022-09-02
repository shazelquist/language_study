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
#
# Space requirements of following plus:
#   Where 'n' is the number of instances in a sentence
#   instance: set(n)
#   following_plus: sum((range(i,n-1)), or 2n?
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
    inspect,
)
from sqlalchemy.orm import relationship, Session, backref
from sqlalchemy.ext.declarative import declarative_base

dburl = environ.get("DB_URI", "sqlite:///ray.db")
temp_path = "../temp/"  # not used directly but by dependent modules
if "jp" in dburl:
    temp_path = "../archive/temp/"  # not used directly but by dependent modules

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
    instance:
    __init__(self, text, freq)

    Maintains text information for calculation and reference

    text    Str    characters, syllables, words
    freq    Int    Number of occurances

    Method properties:
    probability frequency/sum(all instance frequencies)
        Maintained through use of global stale_instance and instance_sum to limit queries for calculation
    total_probability   returns probability as this is already global scope

    Methods:
    update_freq
    add_freq
    """

    __tablename__ = "instance"
    id = Column(Integer, primary_key=True, unique=True)
    text = Column(String, unique=True)
    freq = Column(Integer)
    # prob = Column(Float(unsigned=True))

    def __init__(self, text, freq):
        """
        __init__(self,text,freq)

        Creates new object and sets stale_instance
        """
        global stale_instance
        stale_instance = True
        self.text = text
        self.freq = freq

    def update_freq(self, value):
        """
        update_freq(self, value)

        Updates frequency and sets stale_instance to signal recalculation of total sum.
        """
        global stale_instance
        stale_instance = True
        self.freq = value

    def add_freq(self, value=1):
        """
        add_freq(self, value)

        Updates frequency and instance_sum by adding value
        """
        global instance_sum
        self.freq += value

    @property
    def probability(self):
        """
        probability

        frequency/sum(session.query(instance.freq).all())
        """
        global stale_instance, instance_sum
        self.prob = 0
        if stale_instance:
            instance_sum = sum([i[0] for i in session.query(instance.freq).all()])
            stale_instance = False
        if instance_sum:
            self.prob = self.freq / instance_sum
        return self.prob

    def path(self):
        """
        generates and returns a tuple label of the given text
        """
        return tuple([self.text])

    def total_probability(self):
        """
        total_probability(self)

        returns self.probability as a compatibility between other objects
        """
        return self.probability

    def __repr__(self):
        """
        __repr__(self)

        format = '<{type} id={} text="{}" freq={}, prob={}>'
        """
        return '<{} id={} text="{}" freq={}, prob={}>'.format(
            type(self), self.id, self.text, self.freq, self.probability
        )


class following(Base):
    """
    following

    __init__(parent, child, frequency)

    Given an ancester, keep track of likelyhood of following syllables
    column view of matrix
    needs special terminal cases
    Intended for use in word progression
    """

    __tablename__ = "following"
    id = Column(Integer, primary_key=True, unique=True)
    parent_id = Column(Integer, ForeignKey("instance.id"))
    parent = relationship("instance", primaryjoin="instance.id==following.parent_id")
    text_id = Column(Integer, ForeignKey("instance.id"))
    text = relationship("instance", primaryjoin="instance.id==following.text_id")
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

    @property
    def probability(self):
        """ """
        self.prob = self.freq / sum(
            [
                child.freq
                for child in session.query(following)
                .filter(following.parent_id == self.parent_id)
                .all()
            ]
        )
        return self.prob

    def total_probability(self):
        """ """
        return self.prob * self.parent.probability

    def __repr__(self):
        """ """
        return "<{} id={} parent_id={} child_id={} freq={}>".format(
            type(self), self.id, self.parent_id, self.text_id, self.freq
        )


class tag(Base):
    """
    tag
    __init__(self, tagname)

    A generic tag class for adding descriptive strings to objects

    id      Int     Identifier
    text    Str     Descriptor
    """

    __tablename__ = "tag"
    id = Column(Integer, primary_key=True, unique=True)
    text = Column(String, unique=True)

    def __init__(self, tagname):
        """
        __init__(self,tagname)
        """
        self.text = tagname

    def __repr__(self):
        """
        __repr__(self)

        format = '<{text}>'
        """
        return "<{}>".format(self.text)


class model_source_tags(Base):
    """
    model_source_tags
    __init__(self, ml_id, tag_id)

    id      Int     Garbage Identifier
    ml_id   Int     Foreign Key to model_source
    tag_id  Int     Foreign Key to tag
    """

    __tablename__ = "model_source_tags"
    id = Column(Integer, primary_key=True, unique=True)
    ml_id = Column(Integer, ForeignKey("model_source.id"))
    tag_id = Column(Integer, ForeignKey("tag.id"))

    def __init__(self, ml_id, tag_id):
        """
        __init__(self, ml_id, tag_id):
        """
        self.ml_id = ml_id
        self.tag_id = tag_id

    def __repr__(self):
        """
        __repr__(self)

        format = '<{id}: {ml_id}-{tag_id}>'
        """
        return "<{}: {}-{}>".format(self.id, self.ml_id, self.tag_id)


class model_source(Base):
    """
    model_source
    __init__(self, source, specific=None)

    A collection of locations or addresses from where information was collected
    id          Int     Indentifier
    source      Str     Base source
    specific    Str     Optional more specific source information
        UniqueConstraint(source, specific)

    tags    tag     relationship based on id
    """

    __tablename__ = "model_source"
    id = Column(Integer, primary_key=True, unique=True)
    source = Column(String)  # url, filename, or title
    specific = Column(String, nullable=True)  # url, filename, or title, optional
    UniqueConstraint(source, specific)
    tags = relationship(
        "tag",
        secondary="model_source_tags",
        uselist=True,
    )

    def __init__(self, source, specific=None):
        """ """
        self.source = source
        self.specific = specific

    def __repr__(self):
        return '<id:{} source:"{}":"{}" {}>'.format(
            self.id, self.source, self.specific, self.tags
        )

    def add_tag(self, text):
        """ """
        if not self.id:
            print("Please insert into the database before adding tags")
            exit(1)
        tag_id = session.query(tag).filter(tag.text == text).first().id
        session.add(model_source_tags(ml_id=self.id, tag_id=tag_id))
        return session

    def add_tags(self, texts):
        """ """
        sess = None
        for text in texts:
            sess = self.add_tag(text)
        return sess


class following_plus(Base):
    """
    higher_relation

    __init__(parent_table, parent, child, frequency, degree)

    Given an ancester, keep track of likelyhood of following syllables
    Using parent_table as a reference, we can direct parent queries to higher order

    Properties:
    id          Int         Identifier
    degree      Int         Number of parents
    parent_id   Int         Parent Id, either same type or instance
    freq        Int         Running Count
    this_id     Int         Instance Id, for current relation
    this        Relation    instance relation
        UniqueConstraint(degree, parent_id, this_id)

    Property Methods:
    text        Text relatino from this_id
    parent      Parent object, handled from different types
    child       Child object if exists from the highest freq
    children    Child objects ordered by freq
    probability freq/sum(mutual options)

    Methods:
    children_w          Child objects with a where clause
    total_probability   Probability*total_probability of parents
    path                Generates word tuple of instance text order
    update_freq         Update the probability
    add_freq            Update the probability
    child_sets          Depth first search through children
    """

    __tablename__ = "following_plus"
    id = Column(Integer, primary_key=True, unique=True)
    degree = Column(Integer, nullable=False)
    parent_id = Column(Integer)
    freq = Column(Integer)
    this_id = Column(Integer, ForeignKey("instance.id"))
    this = relationship("instance", primaryjoin="instance.id==following_plus.this_id")
    UniqueConstraint(degree, parent_id, this_id, name="instance_chain")  # onupdate

    @property
    def text(self):
        """
        Returns the text value of the current "this" relation
        """
        return self.this.text

    @property
    def parent(self):
        """
        Returns parent object
        If degree == 1:
            type instance
        elif degree:
            same type, (requires a nonzero degree)
        """
        if self.degree == 1:
            return session.query(instance).filter(instance.id == self.parent_id).first()
        elif self.degree:
            return (
                session.query(following_plus)
                .filter(
                    and_(
                        following_plus.id == self.parent_id,
                        following_plus.degree == self.degree - 1,
                    )
                )
                .first()
            )

    # modifiy to use relationship with function.func if definition, may form cycles if incorrect
    @property
    def child(self):
        """
        Acts like foreign key relationship using the degree to find children
        """
        return (
            session.query(following_plus)
            .filter(
                and_(
                    self.id == following_plus.parent_id,
                    following_plus.degree == self.degree + 1,
                )
            )
            .order_by(following_plus.freq.desc())
            .first()
        )

    def child_sets(self, text=True):
        """
        Depth-first search through children for the tuple sets
        """
        def __r_child__(node,sets,text):
            children = node.children
            if children:
                for chld in children:
                    sets+=__r_child__(chld,sets,text)
            else:
                sets.append(self.path(text))
            return sets
        return __r_child__(self,[],text)

    def export_as(self, order):
        """
        export_as(self, order:list)

        returns a list of properties in the order properties given
        (a better method would be to require actual proper queries in most cases)
        """
        return [getattr(self,prop) for prop in order if hasattr(self,prop)]

    @property
    def children(self):
        """
        Acts like foreign key relationship using the degree to find children
        """
        return (
            session.query(following_plus)
            .filter(
                and_(
                    self.id == following_plus.parent_id,
                    following_plus.degree == self.degree + 1,
                )
            )
            .order_by(following_plus.freq.desc())
            .all()
        )

    def children_w(self, where):
        """
        Acts like foreign key relationship using the degree to find children
        """
        return (
            session.query(following_plus)
            .filter(
                and_(
                    self.id == following_plus.parent_id,
                    following_plus.degree == self.degree + 1,
                    where,
                )
            )
            .order_by(following_plus.freq.desc())
            .all()
        )

    def __init__(self, parent, this, frequency, degree=1):
        """
        __init__(self, parent, this, frequency, degree=1)

        parent:int, this:int, freq:int, degree:int
        """
        self.degree = degree
        self.parent_id = parent
        self.this_id = this
        self.freq = frequency

    def path(self, text=True):
        """
        path(self, text)

        Generates a tuple of given objects from ancester to this

        if text, then generates tuple containing only the text fields
        """

        node = self.parent
        if text:
            path = [self.text]
            while hasattr(node, "degree"):
                path.insert(0, node.text)
                node = node.parent
            path.insert(0, node)  # Notice, if errors occur here then !parent
        else:
            path = [self.this]
            while hasattr(node, "degree"):
                path.insert(0, node.this)
                node = node.parent
            path.insert(0, node)  # Notice, if errors occur here then !parent            
        return tuple(path)

    def update_freq(self, value):
        """
        update_freq(self, value)

        Mutator for the freq property
        """
        self.freq = value

    def add_freq(self, value=1):
        """
        update_freq(self, value=1)

        Mutator for the freq property, adds value with default of 1
        """
        self.freq += value

    @property
    def probability(self):
        """
        Returns the probability of this object given the parent
        """
        self.prob = self.freq / sum(
            [
                child.freq
                for child in session.query(following_plus)
                .filter(
                    and_(
                        following_plus.degree == self.degree,
                        following_plus.parent_id == self.parent_id,
                    )
                )
                .all()
            ]
        )
        return self.prob

    def total_probability(self):
        """
        Returns probability of this object * probability of ancestry
        """
        if not hasattr(self, "prob"):
            self.probability
        return self.prob * self.parent.total_probability()

    def __repr__(self):
        """
        format = '<{type} id={} degree={} parent_id={} child_id={} freq={}>'
        """
        return "<{} id={} degree={} parent_id={} child_id={} freq={}>".format(
            type(self), self.id, self.degree, self.parent_id, self.this_id, self.freq
        )


def main():
    global session
    setup = False
    print(
        "instances {}, following {}".format(
            session.query(instance).count(), session.query(following).count()
        )
    )
    if setup:
        print("creating engine")
        engine = create_engine(dburl)
        print("dropping existing")
        Base.metadata.drop_all(engine)
        print("creating all schemea")
        Base.metadata.create_all(engine)
        print("opening session")
        session = Session(engine)


if __name__ == "__main__":
    main()
