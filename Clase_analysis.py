# -*- coding: utf-8 -*-

import numpy as np
import os
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from skimage import filters
from skimage import filters,morphology
from scipy.optimize import curve_fit


class Analysis:
    def __init__(self, Path, filterset):
        self.path=Path
        self.title=self.path.split('/')[-2]
        self.pos_path=self.path+'Positions/'+os.listdir(self.path+'Positions/')[0]
        self.positions=self.Positions()
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
        
            
    def Positions(self):
        posarray=np.loadtxt(self.pos_path,delimiter=',')
        return posarray
    
    def Ys(self):
        return np.unique(self.positions[:,1])
    
    def Zs(self):
        return np.unique(self.positions[:,2])
    
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
    
    def Thresh(self,nsigma):
        suma=self.Dark(self.filts[0]).flatten()
        suma=suma.flatten()
        for filt in self.filts[1::]:
            imagearray=self.Dark(filt).flatten()
            suma=np.append(suma,imagearray)
        meand,stdd=np.mean(suma),np.std(suma)
        return nsigma*stdd
    
    def Processed_im(self,point,filt,thresh,objectsize=50):
        image=self.Image_dark(point,filt)
        mask=image>thresh
        mask=morphology.remove_small_objects(mask, objectsize)
        mask=mask*1.0
        mask[mask==0]=np.nan
        im=image*mask
        im[np.isnan(im)]=thresh
        im-=thresh
        return im
    
    def Spectrum(self,processed=True,nsigma=3,i_out=np.array([]),scale='linear'):
        store=np.zeros(len(self.wavelengths))
        thresh=self.Thresh(nsigma)
        plt.figure()
        for point in range (1,self.npoints+1):
            if point not in i_out:
                array=np.array([])
                for i,filt in enumerate (self.filts):
                    if processed:
                        im=self.Processed_im(point, filt, thresh)
                    else:
                        im=self.Image_dark(point,filt)
                    s=np.sum(im)
                    array=np.append(array,s/self.widths[i])
                store=np.vstack((store,array))
                plt.plot(self.wavelengths,array,label='Point {}'.format(point))
                plt.scatter(self.wavelengths,(array),marker='x',color='k')
        store=np.delete(store,0,0)
        plt.title(self.title)
        plt.xlabel('$\lambda$ (nm)')
        plt.ylabel('Counts')
        plt.yscale(scale)
        plt.legend()
        return store
    
    def All_points(self,filt,processed=False,nsigma=3):
        fig, axes = plt.subplots(self.ny,self.nz, sharex=True, sharey=True,figsize=(self.ny,self.nz))
        fig.subplots_adjust(0,0,1,1,0,0)
        point=1
        for ax in axes.flat:
            if processed:
                thresh=self.Thresh(nsigma)
                imagearray=self.Processed_im(point,filt,thresh)
            else:
                imagearray=self.Image_dark(point,filt)
            ax.imshow(imagearray,cmap='plasma')
            ax.set_xticks([]),ax.set_yticks([])
            point+=1
            
    def All_points_hist(self,filt,logscale=True,rang=[-100,2000]):
        plt.figure()
        point=1
        for point in range(1,self.npoints+1):
            imagearray=self.Image_dark(point,filt)
            plt.hist(imagearray.flatten(),bins=100,log=logscale,histtype=u'step',range=rang)
            plt.yscale('log')
            point+=1
        plt.axvline(x=self.Thresh(3),linestyle='--',color='k',label='$3\sigma$')
        plt.legend()
            
    def Darks_hist(self,logscale=True,range=[1500,5000]):
        plt.figure()
        for filt in self.filts[1::]:
            imagearray=self.Dark(filt).flatten()
            plt.hist(imagearray,bins=100,log=logscale,histtype=u'step',range=range)
        plt.xlabel('Cuentas')
        plt.ylabel('Numero de pixels')
    
    
    def Plane(self,x,z0,mx,my):
        return z0+mx*x[0]+my*x[1]
        
    def OutOfPlane(self,dif_max=0.1):
        y,z,x=self.positions[:,1],self.positions[:,2],self.positions[:,0]
        popt, pcov = curve_fit(self.Plane, [y,z], x)
        xplane=self.Plane([y,z],popt[0],popt[1],popt[2])
        fig = plt.figure()
        ax = fig.add_subplot(111,projection='3d')
        ax.scatter(self.positions[:,1],self.positions[:,2],self.positions[:,0])
        ax.plot_surface(y.reshape(self.ny,self.nz),z.reshape(self.ny,self.nz),xplane.reshape(self.ny,self.nz),alpha=0.2)
        dif=abs(xplane-x)
        i_out=np.where(dif>dif_max)
        points=np.array([])
        for i in range(len(i_out)):
            points=np.append(points,i_out[i]+1)
        return points
    
    def All_filters(self,point,processed=False,nsigma=3):
        n=len(self.filts)
        fig,ax=plt.subplots(2,int(n/2),figsize=(10,5))
        for i,filt in enumerate (self.filts):
            row=int(i//(n/2))
            col=int(i%(n/2))
            if processed:
                thresh=self.Thresh(nsigma)
                imagearray=self.Processed_im(point,filt,thresh)
            else:
                imagearray=self.Image_dark(point,filt)
            ax[row,col].imshow(imagearray)
            ax[row,col].set_xticks([]),ax[row,col].set_yticks([])
            
            
