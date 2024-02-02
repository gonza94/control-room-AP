"""
This script is to help you with the orbit correction project. It sets up the PyORBIT part of the problem.
You will need the results from the virtual accelerator part for this to work.
"""
import os

from orbit.py_linac.linac_parsers import SNS_LinacLatticeFactory

from orbit.core.bunch import Bunch, BunchTwissAnalysis

from orbit.lattice import AccActionsContainer

from orbit.py_linac.lattice_modifications import Add_quad_apertures_to_lattice
from orbit.py_linac.lattice_modifications import Add_rfgap_apertures_to_lattice

# The sequences we want need for this problem.
names = ["MEBT", "DTL1", "DTL2", "DTL3", "DTL4", "DTL5", "DTL6", "CCL1", "CCL2", "CCL3", "CCL4"]
# The XML file with the structure
xml_file_name = os.environ["HOME"] + "/uspas24-CR/lattice/sns_linac.xml"

# create the factory instance and create the SNS Linac lattice.
sns_linac_factory = SNS_LinacLatticeFactory()
accLattice = sns_linac_factory.getLinacAccLattice(names, xml_file_name)

print("Linac lattice is ready. L=", accLattice.getLength())

# Add apertures to lattice nodes.
aprtNodes = Add_quad_apertures_to_lattice(accLattice)
aprtNodes = Add_rfgap_apertures_to_lattice(accLattice, aprtNodes)

# This adds the kick from the problem statement to the DTL correctors.
DTL_correctors = {'DTL_Mag:DCH618': 0.005, 'DTL_Mag:DCV621': -0.004}
for name, field in DTL_correctors.items():
    DTL_cor = accLattice.getNodeForName(name)
    DTL_cor.setField(field)

# This dictionary connects the model name of the correctors to their nodes so you can change their fields.
# Ex: CCL_correctors[pyorbit_name].setField(new_field)
CCL_DC = { 
'CCL_Mag:DCH104':-0.0001144005119106104, 
'CCL_Mag:DCH106':-0.0004861268657637118, 
'CCL_Mag:DCH110':0.0004712017972386841, 
'CCL_Mag:DCH112': 0.00024949642706947173, 
'CCL_Mag:DCH204':-1.3098911866295336e-05, 
'CCL_Mag:DCH206':2.2014750557422934e-06, 
'CCL_Mag:DCH210':1.0447670161910823e-05, 
'CCL_Mag:DCH212':-4.971646981169682e-06, 
'CCL_Mag:DCH304':-7.663121866380413e-07, 
'CCL_Mag:DCH306':7.470756882053546e-07, 
'CCL_Mag:DCH310':1.394581270873696e-06, 
'CCL_Mag:DCH312':4.0953910345078027e-07, 
'CCL_Mag:DCH402':-4.5871381980433634e-05, 
'CCL_Mag:DCH404':-2.151266392311354e-06, 
'CCL_Mag:DCH406':4.3630952815129924e-05, 
'CCL_Mag:DCH408':6.846732567331265e-05, 
'CCL_Mag:DCH410':-6.162663016983635e-05, 
'CCL_Mag:DCV103' : -0.0025944968103703836, 
'CCL_Mag:DCV105' : 0.0002229832763579651, 
'CCL_Mag:DCV109' : -0.0008517633558972539, 
'CCL_Mag:DCV111' : 0.001507187915494664, 
'CCL_Mag:DCV203' : -7.67185681495367e-06, 
'CCL_Mag:DCV205' : -1.7029878905645898e-06, 
'CCL_Mag:DCV209' : -6.151367063355736e-07, 
'CCL_Mag:DCV211' : 4.8377793292128166e-06, 
'CCL_Mag:DCV303' : -7.81358392310579e-06, 
'CCL_Mag:DCV305' : 5.187980130154673e-06, 
'CCL_Mag:DCV309' : 1.034752918225664e-05, 
'CCL_Mag:DCV311' : 2.7435229431562776e-06, 
'CCL_Mag:DCV401' : 2.0834500835313716e-06, 
'CCL_Mag:DCV403' : 3.2406535810473587e-06, 
'CCL_Mag:DCV405' : 1.5223321380485023e-05, 
'CCL_Mag:DCV407' : 8.329597927871069e-06, 
'CCL_Mag:DCV409' : -1.1244190854161349e-06, 
'CCL_Mag:DCV411' : -1.0425089033856137e-05}

CCL_correctors = {}
quads = accLattice.getQuads()
for quad in quads:
    children = quad.getAllChildren()
    for child_node in children:
        name = child_node.getName()
        if 'DC' in name and 'CCL' in name:
            CCL_correctors[name] = child_node

# Load bunch from file. This bunch is designed to enter the MEBT.
bunch_file = os.environ["HOME"] + "/uspas24-CR/lattice/MEBT_in.dat"
bunch_in = Bunch()
bunch_in.readBunch(bunch_file)

# Decrease the number of particles in the bunch (to speed up simulation and match the virtual accelerator.)
num_part = 1000 # The number of particles you are tracking.
bunch_orig_num = bunch_in.getSizeGlobal()
for n in range(bunch_orig_num):
    if n + 1 > num_part:
        bunch_in.deleteParticleFast(n)
bunch_in.compress()

print("Bunch Generation completed.")

# Set up the lattice cavities
accLattice.trackDesignBunch(bunch_in)

#---- really track the bunch through MEBT
#accLattice.trackBunch(bunch_in)

print("Design tracking completed.")

# Define twiss analysis in case you want to use its functions for your calculations.
twiss_analysis = BunchTwissAnalysis()

# Here is a parameter dictionary in case you want to use it.
my_params = {'old_pos': -1.0, 'count': 0, 'pos_step': 0.1}

# Import AccActionsContainer, a method to add functionality throughout the accelerator.
from orbit.lattice import AccActionsContainer
import numpy as np
from matplotlib import pyplot as plt
pos_array = []
x_array = []
y_array = []

my_container = AccActionsContainer("Bunch Tracking")
pos_start = 0.0

# Here is the action function for you to fill in with your calculations.
def action_entrance(paramsDict):
    node = paramsDict["node"]
    print(node.getName())
    bunch = paramsDict["bunch"]
    pos = paramsDict["path_length"]

    if paramsDict["old_pos"] == pos:
        return
    if paramsDict["old_pos"] + paramsDict["pos_step"] > pos:
        return

    paramsDict["old_pos"] = pos
    paramsDict["count"] += 1

    pos_array.append(pos)

    twiss_analysis.analyzeBunch(bunch)
    x_array.append(twiss_analysis.getAverage(0))
    y_array.append(twiss_analysis.getAverage(2))


def action_exit(paramsDict):
    action_entrance(paramsDict)


# Defining our action container to implement your action while tracking.
#actionContainer = AccActionsContainer("Measure Beam Position along Lattice")
# Add you action to the entrance and exit of each node.
my_container.addAction(action_entrance, AccActionsContainer.ENTRANCE)
my_container.addAction(action_exit, AccActionsContainer.EXIT)

# Track your bunch, passing your actions and parameters.
#accLattice.trackBunch(bunch_in, paramsDict=my_params, actionContainer=actionContainer)
#print("Done tracking!")

# Track the bunch through the lattice. We are also passing our parameter dictionary and action container.
bunch2 = Bunch()
bunch_in.copyBunchTo(bunch2)

# TURN ON CORRECTIONS
for name, field in CCL_DC.items():
	CCL_correctors[name].setField(field)


accLattice.trackBunch(bunch2, paramsDict=my_params, actionContainer=my_container)

# Convert x_array into a numpy array. Then loop through each particle to plot their positions through the lattice.
x_array = np.array(x_array)
#num_of_parts = bunch.getSizeGlobal()
#for n in range(num_of_parts):
plt.plot(pos_array, x_array)
plt.title('Before Correction')
plt.xlabel('Lattice position [m]')
plt.ylabel('Horizontal Position [mm]')
#plt.legend()
plt.show()

  
