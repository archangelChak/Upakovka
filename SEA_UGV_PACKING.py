#!/usr/bin/env python
# coding: utf-8
import pandas as pd 
import numpy as np
import sys
import os
sys.setrecursionlimit(100000)
def CreateCSV(data,filename,PERCOLATION,H_TOTAL=0):
    global used
    filename +=".csv"
    diags_0 = []
    diags_1 = []
    for i in range(len(data)):
        diags_0.append(data[i][0])
        diags_1.append(data[i][1])
    diags_0 = np.vstack(diags_0).T
    diags_1 = np.vstack(diags_1).T

    diag_x, diag_y, diag_z = diags_0[0],diags_0[1],diags_0[2] 
    diag2_x,diag2_y,diag2_z = diags_1[0],diags_1[1],diags_1[2] 
    H_TOTAL=maxheight()
    d = {"SKU_i": dfc['SKU'] ,"x_1^i": diag_x,"y_1^i": diag_y,"z_1^i": diag_z,
         "x_2^i": diag2_x,"y_2^i": diag2_y,"z_2^i": diag2_z,"Aisle":dfc['Aisle'],"Weight":dfc['Weight']}
    df = pd.DataFrame(data=d)
    with open(filename, 'w') as f:
        f.write("%d %f %d\n" % (H_TOTAL,PERCOLATION,0))
        f.close()
    with open(filename, 'a') as f:
        df.to_csv(f, index=False)
def Load(file_name):
    df = pd.read_csv(file_name, skiprows=1,index_col=False)
    return df
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
    global level
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
        prlvl=lvl.copy()
        lvl.clear()
        level+=1
        if (level%2==0):
            place(0,0,nextlevel())
        else:
            placerev(L,W,nextlevel())
    for i in range(len(used)):
        if (used[i]==-1): 
            flag=False
    if (flag): 
        queue.clear()
        return
    return
def placerev(x,y,z):
    global data
    global queue
    global used
    global lvl
    global prlvl
    global level
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
        if ((used[ic]==-1)and(x-dfc['Length'].iloc[ic]>=0)and(y-dfc['Width'].iloc[ic]>=0)and(ic<len(used))):
            data[ic][0][0]=x
            data[ic][0][1]=y
            x1=x-dfc['Length'].iloc[ic]
            y1=y-dfc['Width'].iloc[ic]
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
        x1=x-dfc['Length'].iloc[ic]
        y1=y-dfc['Width'].iloc[ic]
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
        queue.append([x-dfc['Length'].iloc[ic],y,z])
        queue.append([x,y-dfc['Width'].iloc[ic],z])
    if (len(queue)>0): 
        place(queue[0][0],queue[0][1],queue[0][2])
    else:
        prlvl=lvl.copy()
        lvl.clear()
        level+=1
        if (level%2==0):
            place(0,0,nextlevel())
        else:
            placerev(L,W,nextlevel())
    for i in range(len(used)):
        if (used[i]==-1): 
            flag=False
    if (flag): 
        queue.clear()
        return
    return
files = os.listdir('./')
quality=[]
L=1200
W=800
if __name__ == "__main__":
    f2 = sys.argv[1]
    f3= sys.argv[2]
    try:
        level=0
        queue=[]
        lvl=[]
        prlvl=[]
        data=[]
        used=[]
        dfc=Load(f2)
        for i in range(dfc['SKU'].count()):
            for j in range(dfc['Quantity'].iloc[i]-1):
                if (j>0): dfc.append(dfc.iloc[i])
        dfc = dfc.assign(Surface=pd.Series(dfc['Length']*dfc['Width']))
        dfc = dfc.assign(Volume=pd.Series(dfc['Length']*dfc['Width']*dfc['Height']))
        dfc.sort_values(by="Height",inplace=True,ascending=False)
        for i in range(dfc['SKU'].count()):
            used.append(-1)
            data.append([[0,0,0],[0,0,0]])
        place(0,0,0)
        CreateCSV(data=data,filename=f3,PERCOLATION=measurequality())
    except:
        print("Can't open file %s;  \n" % f2)


