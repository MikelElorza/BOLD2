# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 15:33:54 2022

@author: Mikel
"""
from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt

def Plane(x,z0,mx,my):
    return z0+mx*x[0]+my*x[1]

def Max_dev(positions):
    y,z,x=positions[:,1],positions[:,2],positions[:,0]
    popt, pcov = curve_fit(Plane, [y,z], x)
    xplane=Plane([y,z],popt[0],popt[1],popt[2])
    dif=abs(xplane-x)*1000
    i_out=np.where(dif==np.max(dif))[0]
    return i_out,np.max(dif),popt

def Inplane(sample,max_dev):
    pos_out=np.zeros_like(sample.positions[0])
    pos_in=sample.positions
    i_out,dev,popt=Max_dev(pos_in)
    first=True
    while dev>max_dev:
        pos_out=np.vstack((pos_out,pos_in[i_out]))  
        pos_in=np.delete(pos_in,i_out,0)
        i_out,dev,popt=Max_dev(pos_in)
        first=False
    pos_out=np.delete(pos_out,0,0)
    if first:
        pos_out=np.array([])    
    return pos_in,pos_out,dev,popt

def Deviations(sample,positions):
    y,z,x=positions[:,1],positions[:,2],positions[:,0]
    popt, pcov = curve_fit(Plane, [y,z], x)
    xplane=Plane([y,z],popt[0],popt[1],popt[2])
    dif=(xplane-x)*1000
    points=np.array([sample.Position2point(pos) for pos in positions])
    return points, dif
    
def Positions_stats(sample,max_dev=10):
    
    print('___________________________________________________')
    print('')
    print('FOCUS POSITIONS')
    print('___________________________________________________')
    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')
    ax.scatter(sample.positions[:,1],sample.positions[:,2],sample.positions[:,0],marker='x',color='k')
    plt.show()
    
    print('___________________________________________________')
    print('')
    print('FOCUS POSITIONS IN PLANE (maximum deviation of {} microns)'.format(max_dev))
    print('___________________________________________________')
    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')
    pos_in,pos_out,dev,plane_args=Inplane(sample,max_dev)
    ax.scatter(pos_in[:,1],pos_in[:,2],pos_in[:,0],marker='x',color='k')
    zplane=np.array([Plane(point,plane_args[0],plane_args[1],plane_args[2]) for point in sample.positions[:,1:3]])
    ax.plot_surface(sample.positions[:,1].reshape(sample.ny,sample.nz),sample.positions[:,2].reshape(sample.ny,sample.nz),zplane.reshape(sample.ny,sample.nz),alpha=0.2)
    plt.show()
    points_in=np.array([sample.Position2point(pos) for pos in pos_in])
    points_out=np.array([sample.Position2point(pos) for pos in pos_out])
    print('Acceptance = {} microns'.format(max_dev))
    print('Points {} are in the plane'.format(points_in))
    print('Points {} are out of the plane'.format(points_out))
    
    print('___________________________________________________')
    print('')
    print('DEVIATION OF EACH POINT (maximum deviation of {} micras)'.format(max_dev))
    print('___________________________________________________')
    
    fig = plt.figure()
    points,dif=Deviations(sample,pos_in)
    plt.scatter(points,dif,marker='x',color='black')
    plt.axhline(y=0,color='red',linestyle='--')
    plt.xlabel('Point')
    plt.ylabel('Deviation ($\mu$m)')
    

