#!C:/Python_X64/python
#Shane_Hazelquist #Date: Friday, 7/1/2022  #Time: 12:14.19  
#Imports:
from sys import argv
from ray import *
import db_suite as mainself
# Directive:
# 

def erase_db(param=None):
    print("creating engine")
    engine = create_engine("sqlite:///ray.db")
    print("dropping existing")
    Base.metadata.drop_all(engine)
    print("creating all schemea")
    Base.metadata.create_all(engine)
    print("opening session")
    session = Session(engine)


def push_words(target, param=None):
    pass

def push_characters(target, param=None):
    pass

def peek(param=None):
    global session
    print('instances count {}'.format(session.query(instance).count()))
    print('following count {}'.format(session.query(following).count()))
    print('following freq>1 count {}'.format(session.query(following).filter(following.freq>1).count()))

def dump_instance(param=None):
    words=session.query(instance).order_by(instance.freq).all()
    print('all instances:')
    for w in words:
        print(w)

def dump_following(param=None):
    words=session.query(following).order_by(following.freq).all()
    print('all following:')
    for w in words[-20:]:
        print(w,w.parent.text,w.text.text)

def guess_next(param=None):
    query=input('enter a word:')
    word = session.query(instance).filter(instance.text==query).first()
    print('word found status:',word)
    if not word:
        return
    options = session.query(following).filter(following.parent_id==word.id).order_by(following.freq).all()
    print('options status',len(options))
    if not options:
        return
    for child in options:
        print(child.text.text,child.probability())


def main():
    print('starting suite, param:', argv[1:])
    actions = [i[1:] for i in argv if (i and i[0]=='-')]
    print('starting actions',actions)
    print('avaliable actions:',dir(mainself))
    for aindex in range(0,len(actions)):
        action = actions[aindex]
        #index = argv.index('-'+action)
        if action in dir(mainself):
            print('found function "{}"'.format(action))
            getattr(mainself,action)()
        else:
            print('could not find function "{}"'.format(action))
    

if __name__=='__main__':
    main()
