#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
all plotting routines
'''
from IPython.terminal.debugger import set_trace

def plotObsSpectra(xrSpec,ax):
    '''
    plot observed spectra
    Arguments:
        INPUT:
            xrDWR: xarray containing all spectra information (including DWRs with labels "DWR_X_Ka" and "DWR_Ka_W")
        IN- & OUTPUT: 
            ax: axis handle
    '''

    #plot simple spectrum
    colors      = ["b","g","r"]
    labels      = ["X","Ka","W"]
    
    for i_var,var in enumerate(["XSpecH","KaSpecH","WSpecH"]):
        ax.plot(-xrSpec[var]["doppler"],xrSpec[var],color=colors[i_var],label=labels[i_var],lw=1)
        ax.legend()
        ax.set_xlabel("v [m/s]")
        ax.set_ylabel("z [dBz]")
        ax.set_xlim([-0.5,3.0])

    return ax

def plotSpectralDWR(xrDWR,ax):
    '''
    plot the spectral DWR
    Arguments:
        INPUT:
            xrDWR: xarray array containing only the DWR (no matter which frequency)
        IN- & OUTPUT: 
            ax: axis handle
    '''

    ax.plot(-xrDWR.doppler,xrDWR)
    ax.set_xlim([-0.5,2])
    ax.set_xlabel("DV [m/s]")
    ax.set_ylabel("DWR$_{Ka,W}$ [dB]")

    return ax 

def plotSDWRvsDVobs(xrSpec,axes):
    '''
    plot Doppler velocity vs. spectral DWR of X-Ka and Ka-W band combinations (kind of a v-D plot)
    Arguments:
        INPUT:
            xrSpec [can be single spectra or a time-height window]: xarray containing all spectra information (including DWRs with labels "DWR_X_Ka" and "DWR_Ka_W")
                if single spectra: just plot DV vs. DWRs
                if Window:         average over (vertical wind corrected) DV and plot vs DWR
        IN- & OUTPUT: 
            axes: axes handles
    '''

    #these two DWR variables are needed here
    DWRkeys = ["DWR_X_Ka","DWR_Ka_W"]

    xrSpecPlot = xrSpec.copy() #this seems necessary for the way the averaging is applied, but there might be a cleaner way

    if xrSpecPlot["KaSpecH"].values.ndim>1:
        print("plot average DV vs DWR for a time-height window")
        for key in DWRkeys:
            xrSpecPlot[key] = xrSpecPlot[key].mean(dim=["time","range"])
    else:
        print("plot DV vs DWR for a single spectrum")
    
    for i_ax,(ax,key) in enumerate(zip(axes,DWRkeys)):
        axes[i_ax].plot(xrSpecPlot[key],-xrSpecPlot.doppler)
        ax.set_ylabel("DV [m/s]")
    axes[0].set_xlabel("DWR$_{X,Ka}$ [dB]")
    axes[1].set_xlabel("DWR$_{Ka,W}$ [dB]")

    return axes

def plotSDWRvsDVmodel(vel,DWRxk,DWRkw,axes,pType):
    '''
    plot Doppler velocity vs. spectral DWR of X-Ka and Ka-W band combinations (kind of a v-D plot) from the snowScatt simulations
    Arguments:
        INPUT: (all spectral variables)
            vel     [numpy-array]:  velocity [m/s]
            DWRxk   [numpy-array]:  dual-wavelength ratio (X-Ka band) [dB]
            DWRkw   [numpy-array]:  dual-wavelength ratio (Ka-W band) [dB]
            vel     [numpy-array]:  velocity [m/s]
            pType   [str]:          particle-type name
        IN- & OUTPUT: 
            axes: axes handles
    '''

    for i_ax,(ax,DWR) in enumerate(zip(axes,[DWRxk,DWRkw])):
        axes[i_ax].plot(DWR,vel,label=pType)
        ax.set_ylabel("DV [m/s]")

    axes[0].set_xlabel("DWR$_{X,Ka}$ [dB]")
    axes[1].set_xlabel("DWR$_{Ka,W}$ [dB]")

    return axes
