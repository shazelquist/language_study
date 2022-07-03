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

def push_sentence(target, sentence_def param=None):
    
    for sentence in ['source_beg_token']+re.find_all(sentence_def, target)['source_end_token']:
        push_relation(target,param)

def push_relation(target, order=1, param=None):
    
    if order>1:
        push_relation(target,order-1,param)
    if order==1:# push word instances
        for word in ['sentence_beg_token']+re.find_all(sentence_def, target)['sentence_end_token']:
            push_characters(word, param)
    else:# push relation of given order
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

def echo(*param):
    print(param)

def load_dictionary(param=None):
    pass

def main():
    cm_param = argv[1:]
    print('starting suite, param:', cm_param)
    actions = [i[1:] for i in cm_param if (i and i[0]=='-')]
    print('starting actions',actions)
    print('avaliable actions:',dir(mainself))
    while actions:
        print(actions)
        action = actions[0]
        plimit = cm_param.index('-'+action)+1
        while plimit<len(cm_param) and  cm_param[plimit][0]!='-':
            plimit+=1
        print(cm_param[cm_param.index('-'+action)+1:plimit])

        if action in dir(mainself):
            print('found function "{}"'.format(action))
            getattr(mainself,action)(*cm_param[cm_param.index('-'+action)+1:plimit])
        else:
            print('could not find function "{}"'.format(action))

        del actions[0]
        del cm_param[:plimit]
        
    for aindex in range(0,len(actions)):
        action = actions[aindex]
        pstart = cm_param.index('-'+action)
        plimit = len(cm_param)
        if aindex<len(actions):
            plimit = cm_param.index('-'+actions[aindex+1])
        print('splice [{}:{}]'.format(pstart,plimit),cm_param[pstart:plimit])
        #index = cm_param.index('-'+action)
    

if __name__=='__main__':
    main()
