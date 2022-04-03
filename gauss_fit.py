from time import perf_counter
from tkinter.filedialog import askdirectory
from scipy.optimize import curve_fit
from numba import jit
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

@jit
def gauss_1d(x, A, meanx, sigma_x):
    """ 1D Gaussian equation

    Args:
        x (array): Array of x values
        A (float): Amplitude
        meanx (float): Mean of x values
        sigma_x (float): Standard deviation of x values

    Returns:
        Value of Gaussian equation at the inputs
    """

    return A * np.exp(-((x - meanx) ** 2 / sigma_x ** 2))

directory = askdirectory() # Directory GUI
number_of_files = int(input("\nHow many NPC data files are present?\n"))
FWHM = np.zeros([number_of_files, 2])  #  NPCs, 2 FWHM values per NPC
FWHMerr = np.zeros_like(FWHM)
P2P = np.zeros(number_of_files)
P2Perr = np.empty_like(P2P)

start_time = perf_counter() # Start timer function
for i in range(number_of_files):
    plt.figure()
    filename = directory+"/NPCvalues{}.csv".format(i + 1)
    grays = pd.read_csv(filename, usecols=["Gray_Value"])  # y vals
    # read distance column
    distance = pd.read_csv(filename, usecols=["Distance_(µm)"])  # x vals
    x = np.linspace(0, np.max(distance.values[:]), 1000)

    HALF_SIZE = int(np.rint((len(distance.values) / 2))) + 1

    # Two PDFs, so splitting data in half and calculating each PDF separately

    # Mean and std of first half of data

    mu1 = np.mean(distance.values[0:HALF_SIZE])
    std1 = np.std(distance.values[0:HALF_SIZE])
    A1 = np.max(grays.values[0:HALF_SIZE])

    # Mean and std of second half

    mu2 = np.mean(distance.values[HALF_SIZE : HALF_SIZE * 2])
    std2 = np.std(distance.values[HALF_SIZE : HALF_SIZE * 2])
    A2 = np.max(grays.values[HALF_SIZE : HALF_SIZE * 2])

    offst = grays.values[0] # Get offset val

    distance1 = distance.values[0:HALF_SIZE].flatten()
    distance2 = distance.values[HALF_SIZE : HALF_SIZE * 2].flatten()
    grays1 = grays.values[0:HALF_SIZE].flatten()
    grays2 = grays.values[HALF_SIZE : HALF_SIZE * 2].flatten()

    # Generate fit paramets for each half
    popt, pcov = curve_fit(gauss_1d, distance1, grays1, p0=[A1, mu1, std1])
    perr = np.sqrt(np.diag(pcov)) # Errors in fit parameters as defined
    popt2, pcov2 = curve_fit(gauss_1d, distance2, grays2, p0=[A2, mu2, std2])
    perr2 = np.sqrt(np.diag(pcov2)) # Errors in fit parameters as defined
    # Sum the Gaussians into a double Gaussian
    gauss_1dtot = gauss_1d(x, *popt) + gauss_1d(x, *popt2)

    FWHM[i, 0] = 2.355 * popt[2]  # Determine FWHMs
    FWHMerr[i, 0] = 2.355 * perr[2] # Error in FWHM
    FWHM[i, 1] = 2.355 * popt2[2]
    FWHMerr[i, 1] = 2.355 * perr2[2]

    P2P[i] = np.absolute((popt[1] - popt2[1])) # Determine peak to peak distance
    SEM = np.std(P2P) / np.sqrt(4) # Standard error of mean

    # Plotting routine

    plt.plot(x, gauss_1dtot, label="LS Fit {}".format(i))
    plt.plot(
        distance.values[:],
        grays.values[:],
        marker="x",  # add to a single plot
        linestyle="--",
        color="grey",
        label=("NPC {}".format(i)),
    )

    plt.grid()
    plt.xlabel("Distance ($\mu$m)")
    plt.ylabel("Gray Value")
    plt.legend()
    plt.title("NPC {} with LS fit".format(i))
    plt.show()  # Show the generated plot

end_time = perf_counter()
time_taken = end_time - start_time # Time taken


# Print data
print("\n --- DATA --- \n")
print("Mean Peak-to-peak distance = {} µm".format(np.mean(P2P)))
print("\nMean FWHM = ({} ± {}) µm".format(np.mean(FWHM), np.mean(FWHMerr)))
print("\nStandard error of the mean = {}µm\n".format(SEM))
print("Time taken = {} s".format(time_taken))
