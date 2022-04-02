from tkinter.filedialog import askopenfilename
from time import perf_counter
from numba import jit
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb

### Functions

def thunderstorm_file(file_name):
    """ Loads a ThunderSTORM file using the relevant columns for calculating theoretical
    resolution

    Args:
        filename: Name of the file, including path, from a GUI file selection box
    """
    file_data = pd.read_csv(file_name, usecols=["sigma [nm]","intensity [photon]"])

    return file_data["sigma [nm]"].values, file_data["intensity [photon]"].values

def rapidstorm_file(file_name):
    """ Loads a RapidSTORM file using the relevant columns for calculating theoretical
        resolution

    Args:
        filename: Name of the file, including path, from a GUI file selection box
    """
    data = pd.read_csv(file_name, sep=" ", header=None, skiprows = 1)
    data.columns = ["x", "y", "frame", "ADC",
                    "PSFwidthFWHMx", "PSFwidthFWHMy",
                    "FitResidues", "LocalBackground"]

    sigmas = ((data["PSFwidthFWHMx"].values + data["PSFwidthFWHMy"].values) / 2) / 2.355
    return sigmas, data["ADC"]

@jit
def posuncertainty(sigma_vals, intensity_vals):
    """Theoretical resolution estimate, ignoring pixelation or background noise effects

    Args:
        sigma_vals (array): Sigma values from the file
        N (array): Photon number values determined from intensities and ADC conversion

    Returns:
        float: Value for the theoretical resolution (mean position uncertainty) at
               defined sigma and intensity (photon) numbers
    """

    return sigma_vals / np.sqrt(intensity_vals)

###

filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
assert filename[-4:] == ".txt" or filename[-4:] == ".csv", "Please select .txt or csv file"
adc_count = float(input("\nWhat is the value of photoelectrons per AD count?:  \n"))
PLOT_CHOICE = str(input("Would you like visualisation? Y/N: "))

if filename[-4:] == ".csv":
    sigma, intensities = thunderstorm_file(filename)
    photon_number = intensities / adc_count
if filename[-4:] == ".txt":
    sigma, intensities = rapidstorm_file(filename)
    photon_number = intensities / adc_count

# Print data
print(
    "\nPhoton intensities data: \n"
    "\n MEAN {}\n".format(np.mean(intensities)),
    "\n MEDIAN {}\n".format(np.median(intensities)),
    "\n STD {}\n".format(np.std(intensities)),
    "\n MAX {}\n".format(np.max(intensities))
)

## Plotting routine

if PLOT_CHOICE == 'Y':
    sb.set()
    fig = plt.figure()
    ax = sb.histplot(intensities, log_scale = 10)
    plt.axvline(int(np.mean(intensities)), color = 'r',linestyle = '--',
                label = 'Mean = {}'.format(np.round(float(np.mean(intensities)),3)))
    plt.axvline(int(np.median(intensities)), color = 'k',linestyle = '-.',
                label = 'Median = {}'.format(np.round(float(np.median(intensities)),3)))
    plt.ylabel('Count')
    plt.xlabel('Intensity (ADC)')
    plt.xlim(int(np.min(intensities)),int(np.max(intensities)))
    plt.legend()
    plt.tight_layout()
    plt.savefig(fname = '{}histograms.png'.format(str(filename)[:-4]))
    plt.show()

start_time = perf_counter()

res = np.empty(len(photon_number))

# Determine array of resolution values at each sigma
res = [posuncertainty(sigma[i],photon_number[i]) for i, _ in enumerate(res)]

end_time = perf_counter()
time_taken = ((end_time - start_time) / (len(res)/100))

# Print data

print('Mean position uncertainty of {} localizations = {} nm'.format(len(res),np.mean(res)))
print('Time taken per 100 localizations = {}s'.format((time_taken)))
