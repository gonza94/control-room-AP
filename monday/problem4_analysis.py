import numpy as np
import matplotlib.pyplot as plt
import scipy 
from scipy.optimize import curve_fit 

data = np.loadtxt('2024-01-29-17-28.csv',delimiter=',')

def gaussian(x, H, A, x0, sigma): 
    return H + A * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))

ps = data[:,0]
cs = data[:,1]

psprofile = ps[np.multiply(ps>15,ps<45)]
csprofile = cs[np.multiply(ps>15,ps<45)]

popt, cov = curve_fit(gaussian, psprofile, csprofile, p0 = [0,0.3,30,10])

pfit = np.linspace(min(psprofile),max(psprofile),250)
cfit = gaussian(pfit,*popt)

# Plot results
fig,ax = plt.subplots(1,1, figsize = (8,6))

ax.scatter(ps,cs, label = 'VA Data')
ax.plot(pfit,cfit, color = 'cyan', label = 'Gaussian Fit')

ax.set_title(r'Fit: $\sigma=%.4f$  $x_0=%.4f$'%(popt[-1],popt[-2]))
ax.set_xlabel('Slit Position [mm]',fontsize = 30)
ax.set_ylabel('FC Charge [a.u.]',fontsize = 30)

ax.legend()
ax.tick_params(axis='both',labelsize=24)

plt.show()
plt.close()



