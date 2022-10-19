# -*- coding: utf-8 -*-

import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


class Sample:
    def __init__(self, Path, filterset,max_dev=0.01):
        self.path=Path
        self.title=self.path.split('/')[-2]
        self.pos_path=self.path+'Positions/'+os.listdir(self.path+'Positions/')[0]
        self.positions=self.Positions()
        self.positions_in=self.Inplane(max_dev)[0]
        self.positions_out=self.Inplane(max_dev)[1]
        self.points_in=np.array([self.Position2point(position) for position in self.positions_in ])
        self.points_out=np.array([self.Position2point(position) for position in self.positions_out ])
        self.ys=self.Ys()
        self.ny=len(self.ys)
        self.zs=self.Zs()
        self.nz=len(self.zs)
        self.filts=self.Filts()
        self.npoints=len(self.positions[:,0])
        self.positions=self.Positions()
        if filterset==1:
            self.wavelengths0=np.array([420,438,465,503,550,600,650,700,732,800])
            self.widths0=np.array([10.0, 24.0, 30.0, 40.0, 49.0, 52.0, 60.0, 40.0, 68.0, 10.0])
        if filterset==2:
            self.wavelengths0=np.array([400.0, 438.0, 503.0, 549.0, 575.0, 600.0, 630.0, 676.0, 732.0, 810.0])
            self.widths0=np.array([40.0, 24.0,   40.0,   17.0,  15.0,  14.0,  38.0,  29.0,  68.0,  10.0])
        self.wavelengths=np.array([self.wavelengths0[i] for i in self.filts-2])
        self.widths=np.array([self.widths0[i] for i in self.filts-2])
        self.Print()
        
    def Print(self):
        print('')
        print('Sample name='+self.title)
        print('')
        print('Number of points={}'.format(self.npoints))
        print('Points {} are out of the plane, while {} are in the plane'.format(self.points_out,self.points_in))
        fig = plt.figure()
        ax = fig.add_subplot(111,projection='3d')
        ax.scatter(self.positions[:,1],self.positions[:,2],self.positions[:,0])
        print('')
        print('Filterset:')
        print('Wavelengths:{}'.format(self.wavelengths))
        print('Widths:{}'.format(self.widths))
        
    def Positions(self):
        posarray=np.loadtxt(self.pos_path,delimiter=',')
        return posarray
    
    def Point2position(self,point):
        return self.positions[point-1]
    
    def Position2point(self,position):
        if len(position)>0:
            i=np.intersect1d(np.where(position[0]==self.positions[:,0]),(np.where(position[1]==self.positions[:,1])))
            return int(i)+1
    
    def Ys(self):
        return np.unique(self.positions[:,1])
    
    def Zs(self):
        return np.unique(self.positions[:,2])
    
    def Plane(self,x,z0,mx,my):
        return z0+mx*x[0]+my*x[1]

    def Max_dev(self,positions):
        y,z,x=positions[:,1],positions[:,2],positions[:,0]
        popt, pcov = curve_fit(self.Plane, [y,z], x)
        xplane=self.Plane([y,z],popt[0],popt[1],popt[2])
        dif=abs(xplane-x)
        dev=np.mean(np.sqrt(dif**2))
        i_out=np.where(dif==np.max(dif))[0]
        return i_out,dev
    
    def Inplane(self,max_dev):
        pos_out=np.zeros_like(self.positions[0])
        pos_in=self.positions
        i_out,dev=self.Max_dev(pos_in)
        first=True
        while dev>max_dev:
            pos_out=np.vstack((pos_out,pos_in[i_out]))  
            pos_in=np.delete(pos_in,i_out,0)
            i_out,dev=self.Max_dev(pos_in)
            first=False
        pos_out=np.delete(pos_out,0,0)
        if first:
            pos_out=np.array([])    
        return pos_in,pos_out,dev
    
    def Filts(self):
        p=self.path+'Point1/'
        files=os.listdir(p)
        nfilts=np.array([],dtype=int)
        for f in files:
            nfilts=np.append(nfilts,int(f.split('_')[1]))
        return np.sort(nfilts)
    
    def Image(self,point,filt):
        pathp=self.path+'Point{}/'.format(point)
        for file in os.listdir(pathp):
            if 'Filter_{}'.format(filt) in file:
                p=pathp+file
        imagearray=np.loadtxt(p)
        return imagearray
    
    def Dark(self,filt):
        for file in os.listdir(self.path+'Dark/'):
            if 'Filter_{}'.format(filt) in file:
                p=self.path+'Dark/'+file
        darkarray=np.loadtxt(p)
        return darkarray
    
    def Image_dark(self,point,filt):
        im=self.Image(point,filt)
        d=self.Dark(filt)
        return im-d
    