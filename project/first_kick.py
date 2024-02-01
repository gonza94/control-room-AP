# This is an example script using the virtual accelerator.

# Importing epics to use pyepics to talk to Epics
import epics
from epics import pv as pv_channel

# Importing time to allow our script to sleep while we wait for changes to be registered.
import time

# Imports to help with plotting.
import numpy as np
from matplotlib import pyplot as plt

corr_nameH = 'DTL_Mag:PS_DCH618'
corr_nameV = 'DTL_Mag:PS_DCV621'

pv_corr_nameH = pv_channel.PV(corr_nameH+':B_Set')
pv_corr_nameV = pv_channel.PV(corr_nameV+':B_Set')

# PV name for the BPM we want to read.
BPM_VA=['CCL_Diag:BPM101', 'CCL_Diag:BPM103', 'CCL_Diag:BPM112', 'CCL_Diag:BPM202', 'CCL_Diag:BPM212',
        'CCL_Diag:BPM302', 'CCL_Diag:BPM312', 'CCL_Diag:BPM402', 'CCL_Diag:BPM409', 'CCL_Diag:BPM411']

BPMx_PV = []
BPMy_PV = []

for BPM in BPM_VA:
	BPMx_PV.append(pv_channel.PV(f'{BPM}:xAvg'))
	BPMy_PV.append(pv_channel.PV(f'{BPM}:yAvg'))


def get_bpmx():
	readout = []
	for BPMx in BPMx_PV:
		readout.append(BPMx.get())
	return np.array(readout)

def get_bpmy():
	readout = []
	for BPMy in BPMy_PV:
		readout.append(BPMy.get())
	return np.array(readout)

x0 = get_bpmx()
y0 = get_bpmy()

pv_corr_nameH.put(0.005)
pv_corr_nameV.put(-0.004)

time.sleep(2.0)

xnew = get_bpmx()
ynew = get_bpmy()


