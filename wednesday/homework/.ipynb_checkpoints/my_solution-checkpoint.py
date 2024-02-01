"""
This script is the start of the home work where you
will scan a phase of the last MEBT re-buncher RF caity
to find the non-accelerating phase and the cavity amplitude.

>virtual_accelerator --debug  --sequences MEBT

"""

import os
import sys
import math
import time

import numpy
import matplotlib.pyplot as plt

from epics import pv as pv_channel

from orbit.py_linac.linac_parsers import SNS_LinacLatticeFactory
from orbit.py_linac.lattice import MarkerLinacNode
from orbit.utils import phaseNearTargetPhaseDeg

from orbit.core.orbit_utils import Function
from orbit.utils.fitting import PolynomialFit

from uspas_pylib.harmonic_data_fitting_lib import fitCosineFunc

#-------------------------------------------------------------------
#              START of the SCRIPT
#-------------------------------------------------------------------

#-----Parameters at the entrance of MEBT ---------------
# transverse emittances are unnormalized and in pi*mm*mrad
# longitudinal emittance is in pi*eV*sec
e_kin_ini = 0.0025 # in [GeV]
mass = 0.939294    # in [GeV]
gamma = (mass + e_kin_ini)/mass
beta = math.sqrt(gamma*gamma - 1.0)/gamma
print ("relat. gamma=",gamma)
print ("relat.  beta=",beta)
bpm_frequency = 805.0e+6 # MHz
v_light = 2.99792458e+8  # in [m/sec]



names = ["MEBT",]
#---- create the factory instance
sns_linac_factory = SNS_LinacLatticeFactory()

#---- the XML file name with the structure
xml_file_name = os.environ["HOME"] + "/uspas24-CR/lattice/sns_linac.xml"

#---- make lattice from XML file 
accLattice = sns_linac_factory.getLinacAccLattice(names,xml_file_name)

#---- dictionary with the start and end positions of 1st level nodes
node_position_dict = accLattice.getNodePositionsDict()

rf_cavs = accLattice.getRF_Cavities()

#---- we will collect all BPMs accelerator nodes even they are child nodes
bpms = []
for node in accLattice.getNodes():
	if(isinstance(node,MarkerLinacNode) and node.getName().find("BPM") >= 0):
		bpms.append(node)
		continue
	for childNode in node.getBodyChildren():
		if(isinstance(childNode,MarkerLinacNode) and childNode.getName().find("BPM") >= 0):
			bpms.append(childNode)
			continue

#---- now we get the positions of the last cavity and the last BPM
cav_index = len(rf_cavs) - 1
bpm_index = len(bpms) - 1
cav = rf_cavs[cav_index]
bpm = bpms[bpm_index]
bpm_pos = bpm.getPosition()
cav_pos = cav.getPosition()
L_dist = bpm_pos - cav_pos 
print ("========================================")
print ("Cavity = %15s "%cav.getName()," pos[m] = %6.3f "%cav_pos)
print ("BPM    = %15s "%bpm.getName()," pos[m] = %6.3f "%bpm_pos)
print ("========================================")

#-----------------------------------------------------------------
#---- Let's switch off all cavities between cav_index and end
#-----------------------------------------------------------------
for ind in range(cav_index+1,len(rf_cavs) -1):
	cav_amp_pv_tmp = pv_channel.PV("MEBT_LLRF:FCM" + str(ind+1) + ":CtlAmpSet")
	cav_amp_pv_tmp.put(0.)

#------------------------------------------------------------------
#---- Now we perform a phase scan measuring BPM phase
#------------------------------------------------------------------
print("MEBT_LLRF:FCM" + str(cav_index+1))
cav_phase_pv = pv_channel.PV("MEBT_LLRF:FCM" + str(cav_index+1) + ":CtlPhaseSet")
cav_amp_pv   = pv_channel.PV("MEBT_LLRF:FCM" + str(cav_index+1) + ":CtlAmpSet")
bpm_phase_pv = pv_channel.PV("MEBT_Diag:BPM14:phaseAvg")
bpm_amp_pv   = pv_channel.PV("MEBT_Diag:BPM14:amplitudeAvg")

#------------------------------------------------------------------
#---- Performing scan over different cavity phases and getting BPM phases
#------------------------------------------------------------------

phaserange = numpy.linspace(0,360)
bpm_phases_sin = []

for phasei in phaserange:
    print("Setting MEBT_LLRF:FCM" + str(cav_index+1)+ ":CtlPhaseSet to: " + str(phasei))

    cav_phase_pv.put(phasei)

    time.sleep(1.0)

    bpm_phases_sin.append(bpm_phase_pv.get())

bpm_phases_sin = numpy.array(bpm_phases_sin)

dw = mass*beta*((L_dist*2*math.pi*bpm_frequency/v_light)*(numpy.divide(1,bpm_phases_sin))-beta)


# Fit sine function to


#------------------------------------------------------------------
#---- Performing scan over amplitudes at cavities
#------------------------------------------------------------------

time.sleep(10)
amprange = numpy.linspace(0.1,1.2,9)

bpm_ampscan = []

for ampi in amprange:
    
    cav_amp_pv.put(ampi)

    time.sleep(1.0)

    print("Setting MEBT_LLRF:FCM" + str(cav_index+1)+ ":CtlAmp to: " + str(cav_amp_pv.get()))
    cavphaserange = numpy.linspace(-95,-80, 21)

    bpm_cav_ampi = []

    for cavphasei in cavphaserange:
        
        print("Setting MEBT_LLRF:FCM" + str(cav_index+1)+ ":CtlPhaseSet to: " + str(cavphasei))
        cav_phase_pv.put(cavphasei)

        time.sleep(1.0)

        bpm_cav_ampi.append(bpm_phase_pv.get())


    bpm_ampscan.append(bpm_cav_ampi)




