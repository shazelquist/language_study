#!C:/Python_X64/python
#Shane_Hazelquist #Date: Friday, 7/1/2022  #Time: 12:14.19  
#Imports:
from sys import argv
from ray import *
import db_suite as mainself
from json import loads, load
# Directive:
# 

def erase_db(param=None):
    if input('Do you really want to delete & remake {}? y/n\t'.format(dburl))!='y':
        return
    print("creating engine")
    engine = create_engine(dburl)
    print("dropping existing")
    Base.metadata.drop_all(engine)
    print("creating all schemea")
    Base.metadata.create_all(engine)
    print("opening session")
    session = Session(engine)

def push_sentence(target, sentence_defi, param=None):
    
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

def test_following_plus(param=None):
    input("continue? note, this may mess with data in a current db")
    sents=["the quick brown fox jumped over the lazy dog"]
    for sent in sents:
        word_order=sent.split(' ')
        words=[instance(text,0) for text in set(word_order)]
        session.add_all(words)
        session.commit()
        degree=0
        follows={}
        for w in words:
            follows[tuple([w.text])]=w
        print('starting plus parsing with no limit')
        autoid=1
        for i in range(1,len(word_order)+1):
            j = i
            print('index {}, j {}, degree {}'.format(i,j,degree))
            print('\tAiming',word_order[:i+1])
            while j>degree and i<len(word_order):
                print('\tsplice',word_order[:1+j])
                label=tuple(word_order[:1+j])
                print('\tusing label: {} at deg: {}\n\t\t{}'.format(label,degree,[k for k in follows.keys()]))
                if label in follows:
                    print('\t\t\tfound label {}, inc'.format(label))
                    follows[label].update_freq(follows[label].freq+1)
                else:
                    # add object:
                    print('\t\t\tparent label {}'.format(label[:-1]))
                    if j==0:# follows
                        # parent, text, frequency
                        follows[label]=following_plus(follows[label[:-1]].id,follows[tuple([label[-1]])].id,1)
                    else:# plus
                        follows[label]=following_plus(follows[label[:-1]].id,follows[tuple([label[-1]])].id,1,j)
                    follows[label].id=autoid
                    autoid+=1
                j-=1
            degree+=1
    session.add_all([follows[k] for k in follows])
    session.commit()
    for item in session.query(following_plus).order_by(following_plus.degree).all():
        print(item.text.text)

def push_characters(target, param=None):
    pass

def test_data(*param):
    if not param:
        param = input('Please enter a query:')
    for i in param:
        results = session.query(instance).filter(instance.text.startswith(i)).order_by(instance.freq)
        if results.count()<10 or input('{} results found starting with "{}", show all (y)?'.format(results.count(),i))=='y':
            for term in results.all():
                print(term.text,term.freq)

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

def load_dictionary(source=temp_path+'terms.json', param=None):
    with open(source, 'r', encoding='utf-8') as jfile:
        dic_terms = load(jfile)
    existing = [inst.text for inst in session.query(instance).all()]
    print('comparing new objects to existing')
    new_terms = [instance(term, 0) for term in dic_terms if term not in existing]# load as obj
    print('{} new terms to push'.format(len(new_terms)))
    session.add_all(new_terms)
    session.commit()

def test_dictionary():
    print('loading terms')
    terms = loads(open(temp_path+'terms.json','r',encoding='utf-8').read())
    print('comparing db against terms')
    missing = [t.text for t in session.query(instance).all() if t.text not in terms]
    print(missing)
    print('{} terms missing'.format(len(missing)))

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
