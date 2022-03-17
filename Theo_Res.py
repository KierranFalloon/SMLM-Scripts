import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
import scipy
import tkinter as Tk
from tkinter.filedialog import askopenfilename


def ThunderSTORM_file(filename):
    frame = pd.read_csv(filename, usecols=["frame"])
    x = pd.read_csv(filename, usecols=["x [nm]"])
    y = pd.read_csv(filename, usecols=["y [nm]"])
    sigma = pd.read_csv(filename, usecols=["sigma [nm]"])
    intensities = pd.read_csv(filename, usecols=["intensity [photon]"])
    offset = pd.read_csv(filename, usecols=["offset [photon]"])
    bkgstd = pd.read_csv(filename, usecols=["bkgstd [photon]"])
    uncertainty = pd.read_csv(filename, usecols=["uncertainty [nm]"])
    
    return sigma, intensities

def RapidSTORM_file(filename):
    data = pd.read_csv(filename, sep=" ", header=None, skiprows = 1)
    data.columns = ["x", "y", "frame", "ADC", 
                    "PSFwidthFWHMx", "PSFwidthFWHMy", 
                    "FitResidues", "LocalBackground"]
    
    sigmas = ((data["PSFwidthFWHMx"].values + data["PSFwidthFWHMy"].values) / 2) / 2.355
    return sigmas, data["ADC"]

def posuncertainty(sigma,N):
    
    return sigma / np.sqrt(N)

filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
assert filename[-4:] == ".txt" or filename[-4:] == ".csv", "Please select .txt or csv file"

if filename[-4:] == ".csv":
    sigma, intensities = ThunderSTORM_file(filename)
    photon_number = intensities / 3.3
if filename[-4:] == ".txt":
    sigma, intensities = RapidSTORM_file(filename)
    photon_number = intensities / 15.3

 
print(
    "\n MEAN {}\n".format(intensities.mean()),
    "\n MEDIAN {}\n".format(intensities.median()),
    "\n STD {}\n".format(intensities.std()),
    "\n MAX {}\n".format(intensities.max())
)

sb.set()
fig= plt.figure()
sb.histplot(intensities, log_scale = 10)
plt.axvline(int(intensities.mean()), color = 'r',linestyle = '--',label = 'Mean = {}'.format(np.round(float(intensities.mean()),3)))
plt.axvline(int(intensities.median()), color = 'k',linestyle = '-.',label = 'Median = {}'.format(np.round(float(intensities.median()),3)))
plt.ylabel('Count')
plt.xlabel('Intensity (ADC)')
plt.xlim(int(intensities.min()),int(intensities.max()))
#plt.set_title('Logarithmic intensity histogram')
plt.legend()
plt.tight_layout()
plt.savefig(fname = '{}histograms.png'.format(str(filename)[:-4]))
plt.show()

def posuncertainty(sigma_vals,N):
    
    return sigma_vals / np.sqrt(N)

res = np.empty(len(photon_number))
G = np.empty(len(photon_number))
for i in range(len(photon_number)):
    res[i] = posuncertainty(sigma[i],photon_number.values[i])
    
print('MEAN POSITION UNCERTAINTY OF {} POINTS = {} nm'.format(len(res),res.mean()))

