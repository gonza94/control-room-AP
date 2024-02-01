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


# Solve least squares with bounds
lbs = -0.1*np.ones_like(dbxsvd)
ubs = 0.1*np.ones_like(dbxsvd)
resx = lsq_linear(hmat, -xnew, bounds = (lbs,ubs))

lbs = -0.1*np.ones_like(dbysvd)
ubs = 0.1*np.ones_like(dbysvd)
resy = lsq_linear(vmat, -ynew, bounds = (lbs,ubs))



