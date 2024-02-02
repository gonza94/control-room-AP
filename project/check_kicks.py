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

DCH_VA=['CCL_Mag:PS_DCH104',  
'CCL_Mag:PS_DCH106', 
'CCL_Mag:PS_DCH110', 
'CCL_Mag:PS_DCH112', 
'CCL_Mag:PS_DCH204',  
'CCL_Mag:PS_DCH206', 
'CCL_Mag:PS_DCH210', 
'CCL_Mag:PS_DCH212', 
'CCL_Mag:PS_DCH304', 
'CCL_Mag:PS_DCH306', 
'CCL_Mag:PS_DCH310', 
'CCL_Mag:PS_DCH312', 
'CCL_Mag:PS_DCH402', 
'CCL_Mag:PS_DCH404', 
'CCL_Mag:PS_DCH406', 
'CCL_Mag:PS_DCH408', 
'CCL_Mag:PS_DCH410']

DCV_VA=['CCL_Mag:PS_DCV103',
'CCL_Mag:PS_DCV105',
'CCL_Mag:PS_DCV109',
'CCL_Mag:PS_DCV111',
'CCL_Mag:PS_DCV203',
'CCL_Mag:PS_DCV205',
'CCL_Mag:PS_DCV209',
'CCL_Mag:PS_DCV211',
'CCL_Mag:PS_DCV303',
'CCL_Mag:PS_DCV305',
'CCL_Mag:PS_DCV309',
'CCL_Mag:PS_DCV311',
'CCL_Mag:PS_DCV401',
'CCL_Mag:PS_DCV403',
'CCL_Mag:PS_DCV405',
'CCL_Mag:PS_DCV407',
'CCL_Mag:PS_DCV409',
'CCL_Mag:PS_DCV411']

DCH_set = []
DCH_get = []
DCV_set = []
DCV_get = []

for DCH in DCH_VA:
	DCH_set.append(pv_channel.PV(f'{DCH}:B_Set'))
	DCH_get.append(pv_channel.PV(f'{DCH}:B'))
for DCV in DCV_VA:
	DCV_set.append(pv_channel.PV(f'{DCV}:B_Set'))
	DCV_get.append(pv_channel.PV(f'{DCV}:B'))


# PV name for the BPM we want to read.
BPM_VA=['CCL_Diag:BPM101', 'CCL_Diag:BPM103', 'CCL_Diag:BPM112', 'CCL_Diag:BPM202', 'CCL_Diag:BPM212',
        'CCL_Diag:BPM302', 'CCL_Diag:BPM312', 'CCL_Diag:BPM402', 'CCL_Diag:BPM409', 'CCL_Diag:BPM411']

BPMx_PV = []
BPMy_PV = []

BPMamp_PV = []

for BPM in BPM_VA:
	BPMx_PV.append(pv_channel.PV(f'{BPM}:xAvg'))
	BPMy_PV.append(pv_channel.PV(f'{BPM}:yAvg'))

for BPM in BPM_VA:
    BPMamp_PV.append(pv_channel.PV(f'{BPM}:amplitudeAvg'))


def set_dch(ix,B):

	if type(ix)==int:
		for ii,DCH in enumerate(DCH_set):
			if not ii==ix:
				DCH.put(0)
			else:
				DCH.put(B)

	elif len(ix)>1 and len(B)==len(ix):
		for ii in ix:
			DCH_set[ii].put(B[ii])
	time.sleep(1)

def set_dcv(iy,B):

	if type(iy)==int:
		for ii,DCV in enumerate(DCV_set):
			if not ii==iy:
				DCH.put(0)
			else:
				DCH.put(B)
				
	elif len(iy)>1 and len(B)==len(iy):
		for ii in iy:
			DCV_set[ii].put(B[ii])
	time.sleep(1)

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

def get_amp():
    readout = []
    for BPMampi in BPMamp_PV:
        readout.append(BPMampi.get())
    return np.array(readout)


x0 = get_bpmx()
y0 = get_bpmy()

pv_corr_nameH.put(0.005)
pv_corr_nameV.put(-0.004)

time.sleep(2.0)

xnew = get_bpmx()
ynew = get_bpmy()

# ------------------------------
# Calculate possible corrections

import numpy as np
from scipy import linalg
from scipy.optimize import lsq_linear

xnew = np.loadtxt('xerror.txt')
ynew = np.loadtxt('yerror.txt')

hmat = np.loadtxt('orm_x.dat')
hmatpinv = linalg.pinv(hmat)

dbxsvd = hmatpinv@(-xnew)
dbxsvdscaled = dbxsvd/(np.max(np.abs(dbxsvd)))*0.1

dbxlsq = linalg.lstsq(hmat,-xnew)
dbxlsqscaled = dbxlsq[0]/(np.max(np.abs(dbxlsq[0])))*0.1


vmat = np.loadtxt('orm_y.dat')
vmatpinv = linalg.pinv(vmat)

dbysvd = vmatpinv@(-ynew)
dbysvdscaled = dbysvd/(np.max(np.abs(dbysvd)))*0.1

dbylsq = linalg.lstsq(vmat,-ynew)
dbylsqscaled = dbylsq[0]/(np.max(np.abs(dbylsq[0])))*0.1

DCH_str = [-0.00011429907813324256, -0.00048612501901906075, 0.0004712553141769942, 0.00024949642706947173, -1.3098911866295336e-05, 2.2014750557422934e-06, 1.0447670161910823e-05, -4.971646981169682e-06, -7.663121866380413e-07, 7.470756882053546e-07, 1.394581270873696e-06, 4.0953910345078027e-07, -4.5871381980433634e-05, -2.151266392311354e-06, 4.3630952815129924e-05, 6.846732567331265e-05, -6.162663016983635e-05]

DCH_str = [-0.00011429907813324256, -0.00048612501901906075, 0.0004712553141769942, 0.00024949642706947173, -1.3098911866295336e-05, 2.2014750557422934e-06, 1.0447670161910823e-05, -4.971646981169682e-06, -7.663121866380413e-07, 7.470756882053546e-07, 1.394581270873696e-06, 4.0953910345078027e-07, -4.5871381980433634e-05, -2.151266392311354e-06, 4.3630952815129924e-05, 6.846732567331265e-05, -6.162663016983635e-05]

DCV_str = [-0.0025944968103703836, 0.0002229832763579651, -0.0008517633558972539, 0.001507187915494664, -7.67185681495367e-06, -1.7029878905645898e-06, -6.151367063355736e-07, 4.8377793292128166e-06, -7.81358392310579e-06, 5.187980130154673e-06, 1.034752918225664e-05, 2.7435229431562776e-06, 2.0834500835313716e-06, 3.2406535810473587e-06, 1.5223321380485023e-05, 8.329597927871069e-06, -1.1244190854161349e-06, -1.0425089033856137e-05]

# Solve least squares with bounds
lbs = -0.001*np.ones_like(dbxsvd)
ubs = 0.001*np.ones_like(dbxsvd)
resx = lsq_linear(hmat, -xnew, bounds = (lbs,ubs))

lbs = -0.003*np.ones_like(dbysvd)
ubs = 0.003*np.ones_like(dbysvd)
resy = lsq_linear(vmat, -ynew, bounds = (lbs,ubs))

# -------------------------------------------------------

