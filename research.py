import re
import pdb
import sys



def test(categories):
    for name in categories:
        setpat = re.compile(r'\"(.*)\"')
        tmp=setpat.findall(name)
        print(tmp)
        '\n'

if __name__=='__main__':
    f=open(r'category.txt','r')
    categories=[]
    for line in f.read().split('\n'):
        categories=categories+[line]
        '\n'
    del(categories[-1])
    print(len(categories))
    pdb.set_trace()
    test(categories)
