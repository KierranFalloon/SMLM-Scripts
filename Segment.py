import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import numpy as np
import tkinter as Tk
from tkinter.filedialog import askopenfilename
from scipy.optimize import curve_fit
from time import perf_counter

def PDF2D(xytuple, A, meanx, meany, stdx, stdy):
    (bin_centers_x, bin_centers_y) = xytuple
    x, y = np.meshgrid(bin_centers_x, bin_centers_y)
    z = A * np.exp(
        -(
            (x - meanx) ** 2.0 / (2.0 * stdx ** 2.0)
            + (y - meany) ** 2.0 / (2.0 * stdy ** 2.0)
        )
    )
    return z.ravel()


def histogram_gaussian(filename, binsize_pixels):
    """ Fits 2-D Gaussian to a 2-D histogram from data in .csv file

    Args:
        filename (str): File with (weighted) localization data
        binsize_pixels (int): The size of each bin in the histogram in units px. 
    """
    start_time = perf_counter()
    file = pd.read_csv(filename)  # whole file
    x = file["x [nm]"]
    y = file["y [nm]"]

    stdx = np.std(x)
    stdy = np.std(y)

    bins = int(100/binsize_pixels)
    binned_xy, xedges, yedges = np.histogram2d(x, y, bins, normed=False)

    bin_centers_x, bin_centers_y = np.arange(0, bins, 1), np.arange(0, bins, 1)

    # Curve Fit parameters
    popt, pcov = curve_fit(
        PDF2D,
        (bin_centers_x, bin_centers_y),
        binned_xy.ravel(),
        p0=[binned_xy.max(), np.mean(bin_centers_x), np.mean(bin_centers_y), np.std(bin_centers_x), np.std(bin_centers_y)],
        absolute_sigma=True,
    )  # Generate Gaussian parameters from bins as a tuple for x, and the histogram 
    # values as y.
    perr = np.sqrt(np.diag(pcov))
    
    mean = (np.mean(bin_centers_x)+np.mean(bin_centers_y))/2
    sigma = ((np.std(bin_centers_x) + np.std(bin_centers_y))/2)
    fwhm = 2.355*sigma

    mean_fit = (popt[1] + popt[2])/2
    mean_err = perr[0]
    sigma_fit = (popt[3] + popt[4])/2
    sigma_err = perr[1]
    fwhm_fit = 2.355*sigma_fit
    fwhm_err = 2.355*sigma_err

    print("\n",filename[5:-4],"\n")
    print("\nPixel Values: \nFit mean = ({} ± {})px\nFit std = ({} ± {})px\nFit FWHM = ({} ± {})px".format(mean_fit, mean_err, sigma_fit, sigma_err, fwhm_fit, fwhm_err))
    print("\nNanometer Values: \nFit mean = ({} ± {})nm\nFit std = ({} ± {})nm\nFit FWHM = ({} ± {})nm\n".format(mean_fit*binsize_pixels, mean_err*binsize_pixels, sigma_fit*binsize_pixels, sigma_err*binsize_pixels, fwhm_fit*binsize_pixels, fwhm_err*binsize_pixels))
    end_time = perf_counter() # Time to process localizations and create fit parameters
    time_taken = end_time - start_time
    normalized_time = time_taken / (len(x)/100)
    print("Time taken per 100 localization = {}s".format(normalized_time))
    
    if plot_choice == "N":
        return normalized_time
    
    else:

        #Plotting and visualisation routines below
        data_fitted = PDF2D((bin_centers_x, bin_centers_y), *popt) # Fit gaussian

        plt.imshow(binned_xy, cmap=plt.cm.jet, origin="lower")
        plt.colorbar()
        plt.xlabel("x [px]")
        plt.ylabel("y [px]")
        plt.savefig("Images/{}_2d-Histo".format(filename[5:-4]))
        plt.show()


        fig, ax = plt.subplots(1, 1, figsize=(6, 6))
        ax.imshow(
            data_fitted.reshape(bins, bins),
            cmap=plt.cm.jet,
            origin="lower",
            aspect="auto",
            extent=(
                bin_centers_x.min(),
                bin_centers_x.max(),
                bin_centers_y.min(),
                bin_centers_y.max(),
            )
        )
        ax.contour(bin_centers_x, bin_centers_y, data_fitted.reshape(bins, bins), 8, colors="k", linewidths = 0.6)
        mesh = ax.pcolormesh(bin_centers_x, bin_centers_y , data_fitted.reshape(bins,bins))
        fig.colorbar(mesh)
        ax.set_xlabel("x [px]")
        ax.set_ylabel("y [px]")
        #plt.title("2D Histogram with fitted Gaussian")
        plt.savefig("Images/{} 2D Histogram Gaussian".format(filename[5:-4]))
        plt.show()

        X,Y = np.meshgrid(bin_centers_x, bin_centers_y)

        fig = plt.figure()
        ax = plt.axes(projection='3d')
        surf = ax.plot_surface(X,Y,data_fitted.reshape(bins,bins), cmap = 'viridis', edgecolors = 'k', lw = 0.6)
        #plt.title("2D Histogram with fitted surface Gaussian")

        ax.set_xlabel("x [px]")
        ax.set_ylabel("y [px]")
        ax.set_zlabel("Count")
        plt.savefig("Images/{} 2D Histogram surface Gaussian".format(filename[5:-4]))
        plt.show()
        return normalized_time


# 2px / 10nm
#histogram_gaussian("CSVs/Segmented_centred.csv", 5)

## Test Data https://pubs.acs.org/doi/10.1021/acsphotonics.1c00843
plot_choice = "Y"

#histogram_gaussian("CSVs/SMS_10-9M_Gaussian_center_segment.csv", 5)
#histogram_gaussian("CSVs/SMS_10-9M_Gaussian_corner_segment.csv", 5)
#histogram_gaussian("CSVs/SMS_10-9M_MEMS_ON2_8V_1_segment.csv", 5)
#histogram_gaussian("CSVs/SMS_10-9M_MEMS_ON2_8V_1_corner_segment.csv", 5)
histogram_gaussian("CSVs/SMS_10-9_pishaper-filter3_2_segment.csv", 5)
histogram_gaussian("CSVs/SMS_10-9_pishaper-filter3_2_corner_segment.csv", 5)

"""
time10 = 0
for i in range(10):
    plot_choice = "Y"
    time10 += histogram_gaussian("CSVs/SMS_10-9M_Gaussian_corner_segment.csv", 5)
print("Average time per 100 localizations over 10 runs = {}".format(time10/10))
print("Ratio = {}".format(4.710074085*1e-3 / (time10/10)))
"""

#Filename = askopenfilename(title="Open File (csv of with 'x [nm]' and 'y [nm]' columns)", filetypes=[('Comma Separated Values File','*.csv')])
#binsize = int(input("Please enter desired bin size in pixels: "))
#plot_choice = str(input("Would you like visualisation? Y/N: "))
#histogram_gaussian(Filename, binsize)