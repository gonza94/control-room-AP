import os
import sys
import math
import random
import time
import numpy as np
from scipy.optimize import curve_fit
#import pyorbit_cos_fitting_example

#--------------------------------------------
#---- Let's create cos-like data
def function(x):
	"""
	y = Amp*cos(phase + phase_offset) + avg_val
	Parameters:
	phase_offset = -20
	amp = 15
	avg_val = -18.
	"""
	phase = (math.pi/180.)*x
	amp = 15.0
	avg_val = -18.
	phase_offset = -20.0*(math.pi/180.)
	y = amp*math.cos(phase + phase_offset) + avg_val
	return y

x_arr = [1.0*x for x in range(-180,+180,17)]
y_arr = [function(x) for x in x_arr]

#----------------------------------------------
def cosinefunc(x,phase_offset,amp,avg_val):
    phase = (math.pi/180.)*x
    phase_offset = phase_offset*(math.pi/180.)
    y = amp*np.cos(phase + phase_offset) + avg_val
    return y

#---- import fitCosineFunc for fitting
from uspas_pylib.harmonic_data_fitting_lib import fitCosineFunc

tic1 = time.time_ns()

((amp,phase_offset,avg_val),scorer) = fitCosineFunc(x_arr,y_arr,show_progress = False)
print ("(phase_offset,amp,avg_val) = ",(phase_offset,amp,avg_val))

toc1 = time.time_ns()

print('Time Andrei:'+str((toc1-tic1)*1e-6))


tic2 = time.time_ns()
popt, pcov = curve_fit(cosinefunc, x_arr, y_arr, p0=[0.0,np.max(y_arr)/2,np.mean(y_arr)])
print ("(phase_offset,amp,avg_val) = ",(popt))

toc2 = time.time_ns()
print('Time Scipy:'+str((toc2-tic2)*1e-6))




