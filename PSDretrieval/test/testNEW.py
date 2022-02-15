from PSDretrieval import processRadar as pR
from PSDretrieval import plotting as pl
from PSDretrieval import scattering as sc
from PSDretrieval import retrievalUtils as rU
import matplotlib.pyplot as plt
import numpy as np
from snowScatt import snowMassVelocityArea
from IPython.terminal.debugger import set_trace

#define time
date    = "20190113"
time    = "06:18:04"
hRange  = 1600

###load Data
#load spectra
SpecWindow  = pR.loadSpectra()
#SpecWindow  = pR.loadSpectra(loadSample=False,dataPath="/data/obs/campaigns/tripex-pol/processed/",createSample=True,date=date,time=time,tRange=1,hRange=180,hcenter=hRange)

PeaksWindow  = pR.loadPeaks()
#PeaksWindow  = pR.loadPeaks(loadSample=False,dataPath="/data/obs/campaigns/tripex-pol/spectralPeaks/",createSample=True,date=date,time=time,tRange=1,hRange=180,hcenter=hRange)

#get vertical wind information from the Spectral data
SpecWindow = pR.addVerticalWindToSpecWindow(SpecWindow,PeaksWindow)
SpecSingle  = pR.selectSingleTimeHeight(SpecWindow)
SpecSingleWshifted  = pR.shiftSpectra(SpecSingle)

#plot Spectra and sDWR
#fig,ax = plt.subplots(nrows=1,ncols=1)
fig2,axes2 = plt.subplots(nrows=1,ncols=2)
#__ = pl.plotObsSpectra(SpecSingleWshifted,ax)
#__ = pl.plotSDWRvsDVobs(SpecSingle,axes2)
__ = pl.plotSDWRvsDVobs(SpecWindow,axes2)

plt.show()
