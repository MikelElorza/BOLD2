# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 14:00:54 2022

@author: Mikel
"""
import numpy as np
import matplotlib.pyplot as plt
from skimage import morphology

def Processed_im(sample,point,filt,thresh,objectsize=50):
    image=sample.Image_dark(point,filt)
    mask=image>thresh
    mask=morphology.remove_small_objects(mask, objectsize)
    mask=mask*1.0
    mask[mask==0]=np.nan
    im=image*mask
    im[np.isnan(im)]=thresh
    im-=thresh
    return im

def Spectrum(sample,point,processed=True,std=0,nsigma=3,i_out=np.array([]),scale='linear'):
    thresh=std*nsigma
    plt.figure()
    array=np.array([])
    for i,filt in enumerate (sample.filts):
        if processed:
            im=Processed_im(sample,point, filt, thresh)
        else:
            im=sample.Image_dark(point,filt)
        s=np.sum(im)
        array=np.append(array,s/sample.widths[i])
    plt.plot(sample.wavelengths,array,label='Point {}'.format(point))
    plt.scatter(sample.wavelengths,(array),marker='x',color='k')
    plt.title(sample.title)
    plt.xlabel('$\lambda$ (nm)')
    plt.ylabel('Counts')
    plt.yscale(scale)
    plt.legend()
    return array

def Spectrums(sample,processed=True,std=0,nsigma=3,i_out=np.array([]),scale='linear'):
    store=np.zeros(len(sample.wavelengths))
    thresh=std*nsigma
    plt.figure()
    for point in range (1,sample.npoints+1):
        if point not in i_out:
            array=np.array([])
            for i,filt in enumerate (sample.filts):
                if processed:
                    im=Processed_im(sample,point, filt, thresh)
                else:
                    im=sample.Image_dark(point,filt)
                s=np.sum(im)
                array=np.append(array,s/sample.widths[i])
            store=np.vstack((store,array))
            plt.plot(sample.wavelengths,array,label='Point {}'.format(point))
            plt.scatter(sample.wavelengths,(array),marker='x',color='k')
    store=np.delete(store,0,0)
    plt.title(sample.title)
    plt.xlabel('$\lambda$ (nm)')
    plt.ylabel('Counts')
    plt.yscale(scale)
    plt.legend()
    return store      

def Plot_image(im,rangex=[0,512],rangey=[0,512],figsize=(5,5)):
    plt.figure(figsize=figsize)
    im2=im[rangex[0]:rangex[1],rangey[0]:rangey[1]]
    plt.imshow(im2)
    plt.show()

def Plot_processing(sample,point,filt,std,nsigma=3,rangex=[0,512],rangey=[0,512]):
    print('___________________________________________________')
    print('')
    print('DARK')
    print('___________________________________________________')
    d=sample.Dark(filt)
    f,ax=plt.subplots(1,2,figsize=(10,5))
    ax[0].imshow(d),ax[1].hist(d.flatten(),bins=100,log=True)
    plt.show()
    print('___________________________________________________')
    print('')
    print('RAW IMAGE')
    print('___________________________________________________')
    im0=sample.Image(point,filt)
    f,ax=plt.subplots(1,2,figsize=(10,5))
    ax[0].imshow(im0),ax[1].hist(im0.flatten(),bins=100,log=True)
    plt.show()
    print('___________________________________________________')
    print('')
    print('IMAGE-DARK')
    print('___________________________________________________')
    im1=sample.Image_dark(point,filt)
    f,ax=plt.subplots(1,2,figsize=(10,5))
    ax[0].imshow(im1),ax[1].hist(im1.flatten(),bins=100,log=True)
    plt.show()
    print('___________________________________________________')
    print('')
    print('IMAGE-DARK + {}sigma threshold'.format(nsigma))
    print('___________________________________________________')
    thresh=nsigma*std
    mask=im1>thresh
    mask=mask*1.0
    im2=im1*mask
    im2[mask==0]=thresh
    im2-=thresh
    f,ax=plt.subplots(1,2,figsize=(10,5))
    ax[0].imshow(im2),ax[1].hist(im2.flatten(),bins=100,log=True)
    plt.show()
    print('___________________________________________________')
    print('')
    print('IMAGE-DARK + {}sigma threshold + removing small objects'.format(nsigma))
    print('___________________________________________________')
    thresh=nsigma*std
    mask=im1>thresh
    mask=morphology.remove_small_objects(mask, 70)
    mask=mask*1.0
    im2=im1*mask
    im2[mask==0]=thresh
    im2-=thresh
    f,ax=plt.subplots(1,2,figsize=(10,5))
    ax[0].imshow(im2),ax[1].hist(im2.flatten(),bins=100,log=True)
    plt.show()