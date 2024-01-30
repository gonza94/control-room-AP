# Importing epics to use pyepics to talk to Epics
import epics

# Importing time to allow our script to sleep while we wait for changes to be registered.
import time
import sys
import datetime
date_time = datetime.datetime.now()

# Imports to help with plotting.
import numpy as np
from matplotlib import pyplot as plt

def checkSlitFinish():
    setting = epics.caget("slit:Position_Set")
    readback = epics.caget("slit:Position")

    if np.isclose(epics.caget("slit:Position"),epics.caget("slit:Position_Set"),atol=1e-2):
        return True
    else:
        return False

startPos = epics.caget("slit:Position")
finalPos = 50

positions = np.array([])
charges = np.array([])

if not epics.caput("slit:Position_Set",finalPos):
    sys.exit("Couldn't set slit position!")
else: 
    print("Slits are moving!")
    pass

print("Slit Position       Charge")
while checkSlitFinish()==False:
    positioni = epics.caget("slit:Position")
    chargei = epics.caget("FC:charge")

    positions = np.append(positions,positioni)
    charges = np.append(charges,chargei)

    print(positioni,chargei)

    time.sleep(1)

# Set slit back to original position
epics.caput("slit:Position_Set",startPos)

# Save results
data = np.stack((positions,charges),axis=-1)
filetosave = date_time.strftime('%Y-%m-%d-%H-%M')+'.csv'
np.savetxt(filetosave, data, delimiter=",")

# Plot results
fig,ax = plt.subplots(1,1, figsize = (8,6))

ax.scatter(positions,charges)

ax.set_xlabel('Slit Position [mm]',fontsize = 30)
ax.set_ylabel('FC Charge [a.u.]',fontsize = 30)

ax.tick_params(axis='both',labelsize=24)

plt.show()
plt.close()


