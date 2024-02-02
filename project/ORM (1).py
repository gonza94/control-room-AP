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

DCH_set = []
DCH_get = []
DCV_set = []
DCV_get = []
BPMx_PV = []
BPMy_PV = []

for DCH in DCH_VA:
	DCH_set.append(pv_channel.PV(f'{DCH}:B_Set'))
	DCH_get.append(pv_channel.PV(f'{DCH}:B'))
for DCV in DCV_VA:
	DCV_set.append(pv_channel.PV(f'{DCV}:B_Set'))
	DCV_get.append(pv_channel.PV(f'{DCV}:B'))
for BPM in BPM_VA:
	BPMx_PV.append(pv_channel.PV(f'{BPM}:xAvg'))
	BPMy_PV.append(pv_channel.PV(f'{BPM}:yAvg'))


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

	if type(ix)==int:
		for ii,DCV in enumerate(DCV_set):
			if not ii==iy:
				DCH.put(0)
			else:
				DCH.put(B)
				
	elif len(iy)>1 and len(B)==len(iy):
		for ii in iy:
			DCV_set[ii].put(B[ii])
	time.sleep(1)
	
def get_dch():
	return [DCH.get() for DCH in DCH_get]
	
def get_dcv():
	return [DCV.get() for DCV in DCV_get]
	

def get_bpm(dim='x'):
	readout = []
	if dim=='x':
		for BPMx in BPMx_PV:
			readout.append(BPMx.get())
	elif dim=='y':
		for BPMy in BPMy_PV:
			readout.append(BPMy.get())
	return np.array(readout)


def print_bpm(dim='x'):

	print ("======= BPMs before Closing =====")
	if dim=='x':
		for bpm_pv in BPMx_PV:
			print ("BPM PV=",bpm_pv.pvname,\
			" x_avg[mm] = %+12.5g "%bpm_pv.get())
			print ("=================================")
	elif dim=='y':
		for bpm_pv in BPMy_PV:
			print ("BPM PV=",bpm_pv.pvname,\
			" y_avg[mm] = %+12.5g "%bpm_pv.get())
			print ("=================================")
	
	return
	

def orbit_response_matrix(dim='x'):
	set_dch(0,0)
	set_dcv(0,0)
	
	columns = []
	delta = 0.001
	
	if dim=='x':
	
		for ix in range(len(DCH_set)):
			set_dch(ix,delta)
			column = get_bpmx()
			set_dch(ix,-delta)
			column = column - get_bpmx()
			column = column/(2*delta)
			
			columns.append(column[:,None])
	elif dim=='y':
		for iy in range(len(DCV_set)):
			set_dcv(iy,delta)
			column = get_bpmy()
			set_dcv(iy,-delta)
			column = column - get_bpmy()
			column = column/(2*delta)
			
			columns.append(column[:,None])
			
	else:
		print("Error: Function argument (dim) should be 'x' or 'y'")

	return np.hstack(columns)
	
	

set_dch(0,0)
set_dcv(0,0)

pv_channel.PV('DTL_Mag:PS_DCH618:B_Set').put(0.005)
pv_channel.PV('DTL_Mag:PS_DCV621:B_Set').put(-0.004)
time.sleep(1)

"""
#ORM_x = orbit_response_matrix(dim='x')
#np.savetxt('orm_x.dat',ORM_x)
ORM_x = np.loadtxt('orm_x.dat')

#ORM_y = orbit_response_matrix(dim='y')
#np.savetxt('orm_y.dat',ORM_y)
ORM_y = np.loadtxt('orm_y.dat')

print(f'Horizontal ORM has dimensions {ORM_x.shape}')
print(f'Vertical ORM has dimensions {ORM_y.shape}')


set_dch(0,0)
set_dcv(0,0)

svd_x = np.linalg.svd(ORM_x)

plt.plot(svd_x[1])
plt.show()


Ux = svd_x[0]
Vx = svd_x[2].T
Sx = np.zeros((Ux.shape[0],Vx.shape[0]))
Sx[:len(svd_x[1]),:len(svd_x[1])] = np.diag(svd_x[1])

kicks_x = -Vx @ np.linalg.pinv(Sx) @ Ux.T @ get_bpm('x')

print_bpm('x')

set_dch(range(len(kicks_x)),kicks_x)
"""
"""
for ix,DCH in enumerate(DCH_VA):
	print(f'{DCH} Strength Set:  {kicks_x[ix]}')
	print(f'{DCH} Strength:      {pv_channel.PV(DCH+":B").get()}')
"""	


def score(dim='x'):
	ms = 0
	X = get_bpm(dim)
	for x in X
		rms += x**2
	ms /= len(X)
	return np.sqrt(ms)

def jacobian(delta = 0.001):

	jacobi = []
	old_field = get_dch()

	for ix in range(len(DCH_VA)):
		set_dch(ix,old_field[ix]+delta)
		xp = get_bpm('x')
		set_dch(ix,old_field[ix]-delta)
		xm = get_bpm('x')
		jacobi.append((xp-xm)[:,None]/(2*delta))
	
	return np.hstack(jacobi)
	
	

def update_step(lam = 1):

	old_field = get_dch()

	old_score = np.std(get_bpm('x'))

	jacobi = jacobian(0.0001)


	Del = -np.inv(jacobi.T @ jacobi + lam*np.eye(jacobi.shape[1])) @ jacobi.T @ get_bpm('x')
	
	print(f'Old Score is {old_score}')
	print(f'Step is {np.linalg.norm(Del)}')
		
	set_dch(range(len(old_field)), old_field+Del)
	
	print(f'New Score is {score()}')

	return
	

for ii,field in enumerate(bump[:,0]):
	dcv_field_pv_arr[0].put(field)
	time.sleep(2)

	lam = 3
	nu_up = 1.5
	nu_down = 2
	
	old_score = score()	
	update_step()	
	print_DCV()
	print_BPM()

	while score()>1e-2:

		if old_score > score():
			lam *= nu_up
		else:
			lam /= nu_down
			
		update_step()	
		print_DCV()
		print_BPM()
		
		old_score = score()
	
	bump[ii,1] = dcv_field_pv_arr[1].get()
	bump[ii,2] = dcv_field_pv_arr[2].get()
	
print(get_dch())
print_bpm('x')
