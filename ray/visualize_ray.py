#!C:/Python_X64/python
#Shane_Hazelquist #Date: Wednesday, 8/10/2022  #Time: 22:19.35  
#Imports:

# Directive:
# 
from ray import *
from matplotlib import pyplot as plt

def deg_freq():
    x,y=[],[]
    deg=1
    count = session.query(following_plus).filter(following_plus.degree==deg).count()
    x.append(deg)
    y.append(count)
    while count:
        count = session.query(following_plus).filter(following_plus.degree==deg).count()
        x.append(deg)
        y.append(count)        
        deg+=1
    plt.plot(x,y)
    plt.grid()
    plt.show()

def word_links():
    res = session.query(following_plus).filter(following_plus.degree==1).with_entities(following_plus.parent_id,following_plus.this_id).all()
    words = session.query(instance.text).order_by(instance.id).all()
    for link in res:
        plt.plot(link,link[::-1])
    print('items',len(res))
    plt.show()
    
    

def main():
    pass
    word_links()

if __name__=='__main__':
    main()
