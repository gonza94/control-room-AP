import sys
import math
import time
import numpy as np
import datetime
date_time = datetime.datetime.now()

from epics import pv as pv_channel

#-------------------------------------------------------------------
#              START of the SCRIPT
#-------------------------------------------------------------------

#---- DCV01, DCV04, DCV05, DCV10, DCV11, DCV14  
dcv_ind_arr = [1,4,5,10,11,14]
dcv_field_pv_arr = []
for ind in dcv_ind_arr:
	dcv_field_pv_arr.append(pv_channel.PV("MEBT_Mag:PS_DCV"+"%02d"%ind+":B_Set"))

#---- put 0. [T] field in all DCV
for pv in dcv_field_pv_arr:
	pv.put(0.)

#---- BPM01, BPM04, BPM05, BPM10, and BPM11
bpm_ind_arr = [1,4,5,10,11,14]
bpm_ver_pos_pv_arr = []
for ind in bpm_ind_arr:
    bpm_ver_pos_pv_arr.append(pv_channel.PV("MEBT_Diag:BPM"+"%02d"%ind+":yAvg"))

#-------------------------------------------------
#---- Let's print BPM signals before doing bump
#-------------------------------------------------
print ("======= BPMs before Bump =====")
for bpm_pv in bpm_ver_pos_pv_arr:
    print ("BPM PV=",bpm_pv.pvname," y_avg[mm] = %+12.5g "%bpm_pv.get())
print ("=================================")

#---- set DCV01 t0 field 0.05 [T]
dcv01_field = 0.05
dcv_field_pv_arr[0].put(dcv01_field)

#---- give the accelerator time to put beam through MEBT
time.sleep(2.0)	

#---- BPM01, BPM04, BPM05, BPM10, and BPM11
bpm_ind_arr = [1,4,5,10,11,14]
bpm_ver_pos_pv_arr = []
for ind in bpm_ind_arr:
	bpm_ver_pos_pv_arr.append(pv_channel.PV("MEBT_Diag:BPM"+"%02d"%ind+":yAvg"))

#-------------------------------------------------
#---- Let's print BPM signals before bump closing
#-------------------------------------------------
print ("======= BPMs before Closing =====")
for bpm_pv in bpm_ver_pos_pv_arr:
	print ("BPM PV=",bpm_pv.pvname," y_avg[mm] = %+12.5g "%bpm_pv.get())
print ("=================================")


#-------------------------------------------------
#---- Let's do optimization of bump
#-------------------------------------------------
from scipy.optimize import minimize

def objective(x,dcv01_field=0.05):

    dcv_field_pv_arr[0].put(dcv01_field)
    print("Given DCV01 at:   ", dcv_field_pv_arr[0].get())

    dcv04_field = x[0]
    dcv05_field = x[1]

    dcv_field_pv_arr[1].put(dcv04_field)
    dcv_field_pv_arr[2].put(dcv05_field)

    print("Setting DCV04 to:", dcv_field_pv_arr[1].get())
    print("Setting DCV05 to:", dcv_field_pv_arr[2].get())


    #---- give the accelerator time to put beam through MEBT
    time.sleep(1.0)

    # Get Downstream BPMs
    #---- BPM05, BPM10, BPM11 and BPM14
    bpm_ind_arr_down = [5,10,11,14]
    bpm_ver_pos_pv_arr_down = []
    for ind in bpm_ind_arr_down:
        bpm_ver_pos_pv_arr_down.append(pv_channel.PV("MEBT_Diag:BPM"+"%02d"%ind+":yAvg"))

    # Get BPM readings
    print ("======= BPMs Reading at Optimization Step =====")
    bpmreadings = []
    for bpm_pv in bpm_ver_pos_pv_arr_down:
        bpmreading = bpm_pv.get()
        print ("BPM PV=",bpm_pv.pvname," y_avg[mm] = %+12.5g "%bpmreading)
        bpmreadings.append(bpmreading)
    print ("=================================")

    return(np.std(bpmreadings))

dcv01s = np.linspace(0.01,0.05,11)
results = []
allbpmreadings = []
for dcv01i in dcv01s:
    try:
        dcv_field_pv_arr[0].put(dcv01i)
        x0 = 0.05*(np.random.rand(1,2).squeeze()-0.5)
        res = minimize(objective, x0, method='Nelder-Mead', tol=1e-5, args = (dcv01i), options={'disp': True})
        results.append(res)
        
        bpmsi=[]
        for bpm_pv in bpm_ver_pos_pv_arr:
            bpmsi.append(bpm_pv.get())
            #print ("BPM PV=",bpm_pv.pvname," y_avg[mm] = %+12.5g "%bpm_pv.get())
        
        allbpmreadings.append(bpmsi)

    except:
        print("Something went wrong with optimization")


data = np.array([resi.x for resi in results])

objs = [resi.fun for resi in results]

datasave = np.hstack((np.array([dcv01s]).T,data,np.array([objs]).T))

filetosave = date_time.strftime('%Y-%m-%d-%H-%M')+'.csv'
np.savetxt(filetosave,datasave,delimiter=',')




