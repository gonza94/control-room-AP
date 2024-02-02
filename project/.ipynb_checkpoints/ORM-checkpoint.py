import time
import numpy as np
import matplotlib.pyplot as plt

from epics import pv as pv_channel
import epics


DCH_VA=[\
'CCL_Mag:PS_DCH104', \
'CCL_Mag:PS_DCH106', \
'CCL_Mag:PS_DCH110', \
'CCL_Mag:PS_DCH112', \
'CCL_Mag:PS_DCH204', \
'CCL_Mag:PS_DCH206', \
'CCL_Mag:PS_DCH210', \
'CCL_Mag:PS_DCH212', \
'CCL_Mag:PS_DCH304', \
'CCL_Mag:PS_DCH306', \
'CCL_Mag:PS_DCH310', \
'CCL_Mag:PS_DCH312', \
'CCL_Mag:PS_DCH402', \
'CCL_Mag:PS_DCH404', \
'CCL_Mag:PS_DCH406', \
'CCL_Mag:PS_DCH408', \
'CCL_Mag:PS_DCH410']

DCV_VA=[\
'CCL_Mag:PS_DCV103',\
'CCL_Mag:PS_DCV105',\
'CCL_Mag:PS_DCV109',\
'CCL_Mag:PS_DCV111',\
'CCL_Mag:PS_DCV203',\
'CCL_Mag:PS_DCV205',\
'CCL_Mag:PS_DCV209',\
'CCL_Mag:PS_DCV211',\
'CCL_Mag:PS_DCV303',\
'CCL_Mag:PS_DCV305',\
'CCL_Mag:PS_DCV309',\
'CCL_Mag:PS_DCV311',\
'CCL_Mag:PS_DCV401',\
'CCL_Mag:PS_DCV403',\
'CCL_Mag:PS_DCV405',\
'CCL_Mag:PS_DCV407',\
'CCL_Mag:PS_DCV409',\
'CCL_Mag:PS_DCV411']

BPM_VA=['CCL_Diag:BPM101',\
'CCL_Diag:BPM103',\
'CCL_Diag:BPM112',\
'CCL_Diag:BPM202',\
'CCL_Diag:BPM212',\
'CCL_Diag:BPM302',\
'CCL_Diag:BPM312',\
'CCL_Diag:BPM402',\
'CCL_Diag:BPM409',\
'CCL_Diag:BPM411']

DCH_PV = []
DCV_PV = []
BPMx_PV = []
BPMy_PV = []

for DCH in DCH_VA:
	DCH_PV.append(pv_channel.PV(f'{DCH}:B_Set'))
for DCV in DCV_VA:
	DCV_PV.append(pv_channel.PV(f'{DCV}:B_Set'))
for BPM in BPM_VA:
	BPMx_PV.append(pv_channel.PV(f'{BPM}:xAvg'))
	BPMy_PV.append(pv_channel.PV(f'{BPM}:yAvg'))


def set_dch(ix,B):
	for ii,DCH in enumerate(DCH_PV):
		if not ii==ix:
			DCH.put(0)
		else:
			DCH.put(B)
	time.sleep(1)
	
def set_dcv(iy,B):
	for ii,DCV in enumerate(DCV_PV):
		if not ii==iy:
			DCV.put(0)
		else:
			DCV.put(B)
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
	

def orbit_response_matrix(dim='x'):
	set_dch(0,0)
	set_dcv(0,0)
	
	columns = []
	delta = 0.001
	
	if dim=='x':
	
		for ix in range(len(DCH_PV)):
			set_dch(ix,delta)
			column = get_bpmx()
			set_dch(ix,-delta)
			column = column - get_bpmx()
			column = column/(2*delta)
			
			columns.append(column[:,None])
	elif dim=='y':
		for iy in range(len(DCV_PV)):
			set_dch(iy,delta)
			column = get_bpmy()
			set_dch(iy,-delta)
			column = column - get_bpmy()
			column = column/(2*delta)
			
			columns.append(column[:,None])
			
	else:
		print("Error: Function argument (dim) should be 'x' or 'y'")

	return np.hstack(columns)
	
	
pv_channel.PV('DTL_Mag:PS_DCH618:B_Set').put(0.005)
pv_channel.PV('DTL_Mag:PS_DCH621:B_Set').put(-0.004)
time.sleep(1)


#ORM_x = orbit_response_matrix(dim='x')
#np.savetxt('orm_x.dat',ORM_x)
ORM_x = np.loadtxt('orm_x.dat')

#ORM_y = orbit_response_matrix(dim='y')
#np.savetxt('orm_y.dat',ORM_y)
ORM_y = np.loadtxt('orm_y.dat')

print(f'Horizontal ORM has dimensions {ORM_x.shape}')
print(f'Vertical ORM has dimensions {ORM_y.shape}')
