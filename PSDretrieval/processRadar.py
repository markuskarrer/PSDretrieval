#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
reads and processes radar data
'''
import sys
import numpy as np
import pandas as pd
import xarray as xr
import glob
from IPython.core.debugger import set_trace


def getPandasTime(date=None,time=None):
    '''
    get pandas time format from strings of ...
    
    date: date in format yyyymmdd
    time: time in format HH:MM
    '''

    tStep = pd.to_datetime(date+' ' + time)

    return tStep

def regridSpec(data,newVelRes=0.01,windowWidth=10,vRange=[-3,1]):
    #functions from Leonie and Jose's Tripex-pol processing
#-- regrid along the doppler dimension in order to calculate spectral DWR... since we want to smooth the spectra, I am going to interpolate to a finer grid, which will then be smoothed (so we dont loose much information)
# now this is really intricate, but xarray doesnt let me reindex and then rename the doppler coordinate inside of the original dataset... so now we do it like that...
    dataDWR = xr.Dataset()
    newVel = np.arange(vRange[0], vRange[1], newVelRes) #new resolution and doppler velocity vector
    dvX = np.abs(np.diff(data['dopplerX'].values)[0])# normalize spectrum
    X = data['XSpecH']/dvX
    XSpecInt = X.interp(dopplerX=newVel) # interpolate to new vel
    XSpecInt = XSpecInt*newVelRes
    XSpecInt = XSpecInt.rename({'dopplerX':'doppler'})
    print('interp X done')
    dvKa = np.abs(np.diff(data['dopplerKa'].values)[0])
    Ka = data['KaSpecH']/dvKa
    KaSpecInt = Ka.interp(dopplerKa=newVel)
    KaSpecInt = KaSpecInt*newVelRes
    KaSpecInt = KaSpecInt.rename({'dopplerKa':'doppler'})
    print('interp Ka done')
    dvW = np.abs(np.diff(data['dopplerW'].values)[0])
    W = data['WSpecH']/dvW
    WSpecInt = W.interp(dopplerW=newVel)
    WSpecInt = WSpecInt*newVelRes
    WSpecInt = WSpecInt.rename({'dopplerW':'doppler'})
    print('interp W done')
    dataDWR = xr.merge([dataDWR,WSpecInt,KaSpecInt,XSpecInt])
    print('merging datasets done')
    dataDWR = dataDWR.rolling(doppler=windowWidth,min_periods=1,center=True).mean() #smooth dataset

    return dataDWR

def addOffsets(data,data2,test_interp=False):
#functions from Leonie and Jose's Tripex-pol processing
 #- add offset found and the offset calculated during the LV2 processing and the atmospheric attenuation. If you want to test against the LV2 Ze, just set test_interp=True
    data['XSpecH'] = 10*np.log10(data['XSpecH']) + data2.rain_offset_X + data2.offset_x + data2.pia_x
    print('X offsets added')
    data['KaSpecH'] = 10*np.log10(data['KaSpecH']) + data2.rain_offset_Ka +  data2.pia_ka
    data['WSpecH'] = 10*np.log10(data['WSpecH']) + data2.rain_offset_W + data2.offset_w + data2.pia_w
    if test_interp==True:
        data['linKaSpec'] = 10**(data['KaSpecH']/10)
        data['ZeKa'] = data['linKaSpec'].sum(dim='doppler')
        data['Ka_DBZ'] = 10*np.log10(data['ZeKa'])

        data['linWSpec'] = 10**(data['WSpecH']/10)
        data['ZeW'] = data['linWSpec'].sum(dim='doppler')
        data['W_DBZ'] = 10*np.log10(data['ZeW'])
        #dataDWR['W_DBZ_LV0'] = 10*np.log10(data['W_Z_H'])+offsetW+data2.pia_w
        #data1['W_DBZ_H'] = data1['W_DBZ_H']+offsetW+data2.pia_w
        data['linXSpec'] = 10**(data['XSpecH']/10)
        data['ZeX'] = data['linXSpec'].sum(dim='doppler')
        data['X_DBZ'] = 10*np.log10(data['ZeX'])

    data['DWR_X_Ka'] = data['XSpecH'] - data['KaSpecH']
    data['DWR_Ka_W'] = data['KaSpecH'] - data['WSpecH']
    return data

def loadTripexPol(dataPath="/data/obs/campaigns/tripex-pol/processed/",date="20190113",time="06:00",tRange=0,hRange=180,hcenter=1000.):
    '''
    load spectra from Tripex-pol
    ARGUMENTS:
        dataPath:  TODO: 
        date:      TODO: 
        time:      TODO: 
        tRange:        time range to read in [Delta min]
        hRange:        height range to read in [Delta m]
        hcenter:       center of height range [m]
    '''
  
    #convert strings to pandas time format 
    tStep = getPandasTime(date=date,time=time)

    ####load LEVEL1 data
    #get list of files
    dataLV0List = glob.glob(dataPath + "tripex_pol_level_0/" +tStep.strftime('%Y')+'/'+tStep.strftime('%m')+'/'+tStep.strftime('%d')+'/'
                                    +tStep.strftime('%Y')+    tStep.strftime('%m')+    tStep.strftime('%d')+'_*' 
                            '_tripex_pol_3fr_spec_filtered_regridded.nc')
    #load data
    dataLV0 = xr.open_mfdataset(dataLV0List)
    #change time attribute
    dataLV0.time.attrs['units']='seconds since 1970-01-01 00:00:00 UTC'
    #decode according to cf-conventions
    dataLV0 = xr.decode_cf(dataLV0) 
    #select time step
    xrSpec = dataLV0.sel(time=slice(tStep-pd.Timedelta(minutes=tRange/2.),tStep+pd.Timedelta(minutes=tRange/2.)),range=slice(hcenter-hRange/2,hcenter+hRange/2))
    xrSpec = regridSpec(xrSpec,windowWidth=10)

    ####load LEVEL2 data
    dataLV2 = xr.open_mfdataset(dataPath + "tripex_pol_level_2/" + date + '_tripex_pol_3fr_L2_mom.nc')
    #select time step
    dataLV2 = dataLV2.sel(time=slice(tStep-pd.Timedelta(minutes=tRange/2.),tStep+pd.Timedelta(minutes=tRange/2.)))
        
    #get offsets from LV2 data
    xrSpec= addOffsets(xrSpec,dataLV2)
    
    #set_trace()
    #ATTENTION: next lines are just a quick fix. Needs to be replaced!
    #xrSpec["DWR_X_Ka"] = xrSpec["XSpecH"]  - xrSpec["KaSpecH"]
    #xrSpec["DWR_Ka_W"] = xrSpec["KaSpecH"] - xrSpec["WSpecH"]
    xrSpec["KaSpecHspecNoise"] = -47.
    xrSpec["XSpecHspecNoise"] = -47.
    xrSpec["pa"] = 90000.

    #xrSpec = addOffsets(xrSpec,dataLV2selt) #TODO:
    #TODO: add DWRs #is done in ZFR_riming/plotRoutines

    return xrSpec

def loadSpectra(loadSample=True,dataPath=None,createSample=False,date="20190113",time="06:00",tRange=5,hRange=180,hcenter=1000):
    '''
    load Doppler spectra data

    loadSample: 
        if True: load processed data from sample_data directory
        if False: load data from path
    dataPath: path to the spectra files
    createSample:  TODO 
    tRange:        time range to read in [Delta min]
    hRange:        height range to read in [Delta m]
    hcenter:       center of height range [m]
    '''
    import xarray as xr
    from os import path
    
    this_dir = path.dirname(path.realpath(__file__)) #path of this script

    if loadSample:
        xrSpec = xr.open_dataset(this_dir + "/sample_data/20190122_1455_1000m.nc") #this is window with several times and heights
    else:
        if dataPath is None:
            print("error: provide path to radar data if loadSample=False")
            sys.exit(0)
        else: 
            '''
            load a spectra file
            '''
            if "tripex-pol" in dataPath:
                print("load file:"  + dataPath)
                xrSpec = loadTripexPol(dataPath="/data/obs/campaigns/tripex-pol/processed/",date=date,time=time,tRange=tRange,hcenter=hcenter,hRange=hRange)
            else:
                print("error: the path is not found or the file is not in the right format")
                sys.exit(0)

    return xrSpec

def createSample(dataPath):
    '''
    create a sample from the tripex-pol files
    ATTENTION: this works only on igmk-server
    '''

def selectSingleTimeHeight(xrSpec,centered=True,time=None,height=None):
    '''
    select data from a single time-height pixel

    centered:
            True: get data from center in time and range space
            False: provide time and height (TODO: what format??)
    '''


    if centered:
        centeredTime    = xrSpec.time[0] + (xrSpec.time[-1] - xrSpec.time[0])/2.
        centeredHeight  = xrSpec.range[0] + (xrSpec.range[-1] - xrSpec.range[0])/2.
        xrSpecSingle    = xrSpec.sel(time=centeredTime,range=centeredHeight,method="nearest")
    else:
        if (time is None) or (height is None):
            print("time or height cant be None when centered=False")
        else:
            print("TODO: implement time and height selection")

    return xrSpecSingle
