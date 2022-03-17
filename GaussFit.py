# Diameter and FWHM of NPCs

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate.fitpack2 import InterpolatedUnivariateSpline
from scipy.stats import norm
from scipy.interpolate import interp1d
from scipy import interpolate
import tkinter as Tk
from tkinter.filedialog import askopenfilename
from scipy.optimize import curve_fit


def PSF(x, A, x_c, sigma_x):

    return A * np.exp(-((x - x_c) ** 2 / sigma_x ** 2))


# + (y-y_c)**2/sigma_y**2)

names = [100, 300, 1000, 3000]
plotnames = ["noisy", "not noisy"]

""" Nuclear Pore Complex Analysis """

for i in range(10):
    plt.figure()
    filename = "CSVs/NPCvalues{}.csv".format(i + 1)
    grays = pd.read_csv(filename, usecols=["Gray_Value"])  # y vals
    # read distance column
    distance = pd.read_csv(filename, usecols=["Distance_(µm)"])  # x vals
    FWHM = np.zeros([10, 2])  #  NPCs, 2 FWHM values per NPC
    P2P = np.zeros(10)
    x = np.linspace(0, np.max(distance.values[:]), 1000)

    halfsize = int(np.rint((len(distance.values) / 2))) + 1

    # Two PDFs, so splitting data in half and calculating each PDF separately

    # Mean and std of first half of data
    mu1 = np.mean(distance.values[0:halfsize])
    std1 = np.std(distance.values[0:halfsize])
    A1 = np.max(grays.values[0:halfsize])

    # Mean and std of second half

    mu2 = np.mean(distance.values[halfsize : halfsize * 2])
    std2 = np.std(distance.values[halfsize : halfsize * 2])
    A2 = np.max(grays.values[halfsize : halfsize * 2])

    """ LS Fitting routine """
    offst = grays.values[0]

    distance1 = distance.values[0:halfsize].flatten()
    distance2 = distance.values[halfsize : halfsize * 2].flatten()
    grays1 = grays.values[0:halfsize].flatten()
    grays2 = grays.values[halfsize : halfsize * 2].flatten()

    popt, pcov = curve_fit(PSF, distance1, grays1, p0=[A1, mu1, std1])
    popt2, pcov2 = curve_fit(PSF, distance2, grays2, p0=[A2, mu2, std2])
    PSFtot = PSF(x, *popt) + PSF(x, *popt2)

    FWHM[i, 0] = 2.355 * popt[2]  # np.std(distance.values[0:halfsize])
    FWHM[i, 1] = 2.355 * popt2[2]  # np.std(distance.values[halfsize:halfsize*2])

    P2P[i] = np.absolute((popt[1] - popt2[1]))
    SEM = np.std(P2P) / np.sqrt(4)

    """ Plotting routine """

    plt.plot(x, PSFtot, label="LS Fit {}".format(i))
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
    plt.savefig(fname="PNGs/NPC_PSF_{}".format(i))
    # plt.show()  # Show the generated plot

print("\n --- Nuclear Pore Complex with Least Squares Fit DATA --- \n")
print("Mean Peak-to-peak distance = {} µm".format(np.mean(P2P)))
print("\nMean FWHM = {} µm".format(np.mean(FWHM)))
print("\nStandard error of the mean = {}µm\n".format(SEM))


""" Structure Ratio Analysis """

for l in range(2):
    plt.figure()
    # Loops through and merges the 4 NPC line profile datas into one array
    # In each loop, adds that data to a plot for comparison of each NPC
    for i in range(4):  # number of NPCs
        j = i + 1  # indexing starts at 0, but files named from 1
        filename = "CSVs/NPCvalues{}_{}.csv".format(j, l + 1)  # select file
        # read gray values column
        grays = pd.read_csv(filename, usecols=["Gray_Value"])  # y vals
        # read distance column
        distance = pd.read_csv(filename, usecols=["Distance_(µm)"])  # x vals

    FWHM = np.zeros([4, 2])  #  NPCs, 2 FWHM values per NPC
    P2P = np.zeros(4)

    x = np.linspace(0, 0.2, 1000)
    for i in range(4):  # number of NPCs
        plt.figure()
        j = i + 1  # indexing starts at 0, but files named from 1
        filename = "CSVs/NPCvalues{}_{}.csv".format(j, l + 1)
        # read distance column
        distance = pd.read_csv(filename, usecols=["Distance_(µm)"])
        # read gray values column
        grays = pd.read_csv(filename, usecols=["Gray_Value"])
        PSF1 = np.zeros(len(distance))
        PSF2 = np.zeros(len(distance))
        PSFtot = np.zeros_like(PSF1)
        halfsize = int(np.rint((len(distance.values) / 2))) + 1
        # Two PDFs, so splitting data in half and calculating each PDF separately

        # Mean and std of first half of data
        # mu1 = distance.values[grays.values[0:halfsize].argmax()] # mean of gaussian = max of NPC
        mu1 = np.mean(distance.values[0:halfsize])
        # std1 = np.sqrt(np.sum(np.abs(distance.values[int(0.25*halfsize):int(0.75*halfsize)]-mu1)**2/halfsize)) # standard deviation of gaussian =
        std1 = np.std(distance.values[0:halfsize])
        A1 = np.max(grays.values[0:halfsize])

        # Mean and std of second half
        # mu2, std2 = norm.fit(distance.values[halfsize-1:(halfsize*2)])
        # mu2 = distance.values[halfsize + grays.values[halfsize:halfsize*2].argmax()]
        mu2 = np.mean(distance.values[halfsize : halfsize * 2])
        # std2 = np.sqrt(np.sum(np.abs(distance.values[int(1.25*halfsize):int(1.75*halfsize*2)]-mu2)**2/halfsize))
        std2 = np.std(distance.values[halfsize : halfsize * 2])
        A2 = np.max(grays.values[halfsize : halfsize * 2])

        offst = grays.values[0]

        distance1 = distance.values[0:halfsize].flatten()
        distance2 = distance.values[halfsize : halfsize * 2].flatten()
        grays1 = grays.values[0:halfsize].flatten()
        grays2 = grays.values[halfsize : halfsize * 2].flatten()
        popt, pcov = curve_fit(PSF, distance1, grays1, p0=[A1, mu1, std1])
        popt2, pcov2 = curve_fit(PSF, distance2, grays2, p0=[A2, mu2, std2])
        PSFtot = PSF(x, *popt) + PSF(x, *popt2)

        FWHM[i, 0] = 2.355 * popt[2]  # np.std(distance.values[0:halfsize])
        FWHM[i, 1] = 2.355 * popt2[2]  # np.std(distance.values[halfsize:halfsize*2])

        P2P[i] = np.absolute((popt[1] - popt2[1]))
        SEM = np.std(P2P) / np.sqrt(4)

        """ Plotting routine """
        # plt.plot(distance.values[:], grays.values[:],
        #    label=("NPC {}".format(names[i])), marker='x', linestyle='None')
        # plt.plot(distance.values[:], PSF1[:], label='PSF 1')
        # plt.plot(distance.values[:], PSF2[:], label='PSF 2')
        plt.plot(x, PSFtot, label="LS Fit {}".format(names[i]))
        plt.plot(
            distance.values[:],
            grays.values[:],
            marker="x",  # add to a single plot
            linestyle="--",
            color="grey",
            label=("Data {}".format(names[i])),
        )

        plt.grid()
        plt.xlabel("Distance ($\mu$m)")
        plt.ylabel("Gray Value")
        plt.legend()
        plt.title("Structure Ratio {} - {}".format(i, plotnames[l]))
        plt.savefig(fname="PNGs/Structure Ratio {} - {}".format(i, plotnames[l]))
        # plt.show()  # Show the generated plot

    print("\n --- Structure Ratio {} DATA --- \n".format(plotnames[l]))
    print("Mean Peak-to-peak distance = {} µm".format(np.mean(P2P)))
    print("\nMean FWHM = {} µm".format(np.mean(FWHM)))
    print("\nStandard error of the mean = {}µm\n".format(SEM))
