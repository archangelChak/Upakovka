
# coding: utf-8

# In[8]:


import pandas as pd #библиотека для работы с бд
import numpy as np #матбиблиотека
from shapely.geometry import Polygon
import sys
sys.setrecursionlimit(100000)
quality=[]
num=0
f1=open('COS-TEST-1-in.csv','r')
f2=open('Output.csv','w')
s=f1.readlines()
print(s[1][:len(s[1])-1],file=f2)
for line in np.arange(2,len(s),1):
    print(s[line][:len(s[line])-2],file=f2)
f1.close()
f2.close()
L=1200
W=800
wtf=0
queue=[]
lvl=[]
prlvl=[]
def maxheight():
    global data
    z=[]
    for placement in data:
        z.append(placement[1][2])
    height=max(z)
    return height
def nextlevel():
    global data
    z=[]
    for placement in data:
        if((placement[0][0]==0)and(placement[0][1]==0)): z.append(placement[1][2])
    return max(z)
def measurequality():
    height=maxheight()
    global W
    global L
    global dfc
    global used
    volume=0
    for i in range(len(used)):
        if (used[i]==1): volume+=dfc['Surface'].iloc[i]*dfc['Height'].iloc[i]
    summ= W * L *height
    return volume/summ
def fit(x,y,z,index):
    global data
    global lvl
    global wtf
    global dfc
    for inc in range(len(used)):
        if (used[inc]==1):
            if ((x>=data[inc][1][0])or(x+dfc['Length'].iloc[index]<=data[inc][0][0])):
                continue
            elif ((y>=data[inc][1][1])or(y+dfc['Width'].iloc[index]<=data[inc][0][1])):
                continue
            elif ((z>=data[inc][1][2])or(z+dfc['Height'].iloc[index]<=data[inc][0][2])):
                continue
            else:
                if (wtf):
                    print(x,y,z,x+dfc['Length'].iloc[index],y+dfc['Width'].iloc[index],z+dfc['Height'].iloc[index])
                    print(data[inc][0][0],data[inc][0][1],data[inc][0][2],data[inc][1][0],data[inc][1][1],data[inc][1][2],inc)
                    print('False')
                return False
    return True
def floorfinder(x,y,z,x1,y1):
    global data
    global prlvl
    floor=[]
    for inc in prlvl:
        t1=(x>=data[inc][1][0])or(x1<=data[inc][0][0])
        t2=(y>=data[inc][1][1])or(y1<=data[inc][0][1])
        if (not (t1 or t2)):
            floor.append(data[inc][1][2])
    if (len(floor)>0):
        z=max(floor)
    return z
def place(x,y,z):
    global data
    global queue
    global used
    global lvl
    global prlvl
    global wtf
    global dfc
    global L
    global W
    flag=True
    if (len(queue)>0): queue.pop(0)
    maxqual=0
    qual=[]
    index=[]
    for i in range(len(used)):
        if (used[i]==-1): 
            flag=False
    if (flag): 
        queue.clear()
        return
    for ic in range(len(used)):
        if ((used[ic]==-1)and(x+dfc['Length'].iloc[ic]<=L)and(y+dfc['Width'].iloc[ic]<=W)and(ic<len(used))):
            data[ic][0][0]=x
            data[ic][0][1]=y
            x1=x+dfc['Length'].iloc[ic]
            y1=y+dfc['Width'].iloc[ic]
            if (z==0):
                data[ic][0][2]=z
            else:
                z=floorfinder(x,y,z,x1,y1)
            if(fit(x,y,z,ic)):
                data[ic][0][2]=z
                z1=z+dfc['Height'].iloc[ic]
                data[ic][1][0]=x1
                data[ic][1][1]=y1
                data[ic][1][2]=z1
                used[ic]=1
                qual.append(measurequality())
                data[ic]=[[0,0,0],[0,0,0]]
                used[ic]=-1
                index.append(ic)
            else:
                data[ic]=[[0,0,0],[0,0,0]]
    if (len(index)>0):
        ic=index[qual.index(max(qual))]
        lvl.append(ic)
        data[ic][0][0]=x
        data[ic][0][1]=y
        x1=x+dfc['Length'].iloc[ic]
        y1=y+dfc['Width'].iloc[ic]
        if (z==0):
            data[ic][0][2]=z
        else:
            z=floorfinder(x,y,z,x1,y1)
        data[ic][0][2]=z
        z1=z+dfc['Height'].iloc[ic]
        data[ic][1][0]=x1
        data[ic][1][1]=y1
        data[ic][1][2]=z1
        used[ic]=1
        queue.append([x+dfc['Length'].iloc[ic],y,z])
        queue.append([x,y+dfc['Width'].iloc[ic],z])
    if (len(queue)>0): 
        place(queue[0][0],queue[0][1],queue[0][2])
    else:
        if (nextlevel()==1602):
            wtf=1
        print(nextlevel())
        prlvl=lvl.copy()
        print(prlvl)
        lvl.clear()
        place(0,0,nextlevel())
    for i in range(len(used)):
        if (used[i]==-1): 
            flag=False
    if (flag): 
        queue.clear()
        return
    return
data=[]
used=[]
dfc=pd.read_csv('Output.csv')
dfc.sort_values(by="Height",inplace=True,ascending=False)
for i in range(dfc['SKU'].count()):
    for j in range(dfc['Quantity'].iloc[i]-1):
        if (j>0): dfc.append(dfc.iloc[i])
j=dfc['SKU'].count()-1
i=0
dfc = dfc.assign(Surface=pd.Series(dfc['Length']*dfc['Width']))
dfc = dfc.assign(Volume=pd.Series(dfc['Length']*dfc['Width']*dfc['Height']))
volume=dfc['Volume'].sum()
dfc.sort_values(by="Height",inplace=True,ascending=False)
for i in range(dfc['SKU'].count()):
    used.append(-1)
    data.append([[0,0,0],[0,0,0]])
place(0,0,0)
f3=open('COS-TEST-1-out.csv','w')
for i in range(len(used)):
    print(dfc['SKU'].iloc[i],data[i][0][0],data[i][0][1],data[i][0][2],data[i][1][0],data[i][1][1],data[i][1][2],dfc['Aisle'].iloc[i],dfc['Mass'].iloc[i],sep=",",file=f3)
f3.close()

