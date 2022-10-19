# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 10:06:48 2022

@author: Mikel
"""
import numpy as np
import matplotlib.pyplot as plt
import os


def Dark(sample,filt):
    sample.Dark(filt)

def Dark_mean(sample):
    suma=sample.Dark(sample.filts[0])
    suma=suma
    for filt in sample.filts[1::]:
        imagearray=sample.Dark(filt)
        suma=suma+imagearray
    dm=suma/len(sample.filts)
    return dm

def Standard_deviation(sample):
    dm=Dark_mean(sample)
    suma=np.array([])
    for filt in sample.filts[1::]:
        imagearray=(sample.Dark(filt)-dm).flatten()
        suma=np.append(suma,imagearray)
    return np.std(suma)
    
def Dark_stats(sample):
    dm=Dark_mean(sample)
    suma=np.array([])
    suma=suma.flatten()
    means=np.array([])
    stds=np.array([])
    print('___________________________________________________')
    print('')
    print('INDIVIDUAL DARKS')
    print('___________________________________________________')
    for filt in sample.filts:
        mean=np.mean(sample.Dark(filt))
        means=np.append(means,mean)
        std=np.std(sample.Dark(filt))
        stds=np.append(stds,std)
    fig,ax=plt.subplots(1,2,figsize=(10,5))
    ax[0].scatter(sample.filts,means,marker='x',color='k')
    ax[0].axhline(y=np.mean(means),linestyle='--',color='red')
    ax[0].set_xlabel('Filter')
    ax[1].set_xlabel('Filter')
    ax[1].scatter(sample.filts,stds,marker='x',color='k')
    ax[1].axhline(y=np.mean(stds),linestyle='--',color='red')
    print('Mean of means = {}'.format(np.mean(means)))
    print('Standard deviation of means = {}'.format(np.std(means)))
    print('Mean of standard deviations = {}'.format(np.mean(stds)))
    print('Standard deviation of standard deviations = {}'.format(np.std(stds)))
    plt.show()
    
    print('___________________________________________________')
    print('')
    print('MEAN OF DARKS')
    print('___________________________________________________')
    fig,ax=plt.subplots(1,2,figsize=(10,5))
    ax[0].imshow(dm)
    ax[1].hist(dm.flatten(),bins=100,log=True,histtype=u'step')
    ax[0].set_title('Image of mean')
    ax[1].set_title('Histogram of mean')
    print('Mean = {} counts'.format(np.mean(dm)))
    print('Standard Deviation = {} counts'.format(np.std(dm.flatten())))
    plt.show()
    print('___________________________________________________')
    print('')
    print('DEVIATION FROM THE MEAN')
    print('___________________________________________________')
    fig,ax=plt.subplots(1,2,figsize=(10,5))
    for filt in sample.filts:
        imagearray=(sample.Dark(filt)-dm).flatten()
        suma=np.append(suma,imagearray)
        ax[1].hist(imagearray,bins=100,log=True,histtype=u'step',range=[-300,300],label='Filter {}'.format(filt))
    ax[0].hist(suma,bins=100,log=True,histtype=u'step',range=[-300,300],label='Filter {}'.format(filt))
    meand,stdd=np.mean(suma),np.std(suma)
    ax[0].set_title('Deviation from mean (all filters)')
    ax[1].set_title('Deviation from mean (by filter)')
    plt.legend()
    plt.show()
    print('Std= {} counts'.format(stdd))


    