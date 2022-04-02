from time import perf_counter
from tkinter.filedialog import askopenfilename
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def gauss_2d(xytuple, A, meanx, meany, stdx, stdy):
    """ 2D Gaussian equation

    Args:
        xytuple (tuple): Tuple of x and y values
        A (float): Amplitude of Gaussian
        meanx (float): Mean of x values
        meany (float): Mean of y values
        stdx (float): Standard deviation of x values
        stdy (float): Standard deviation of y values

    Returns:
        Value of 2D Gaussian in the form [x,y]
    """
    (bin_centers_x, bin_centers_y) = xytuple
    x, y = np.meshgrid(bin_centers_x, bin_centers_y)
    z = A * np.exp(
        -(
            (x - meanx) ** 2.0 / (2.0 * stdx ** 2.0)
            + (y - meany) ** 2.0 / (2.0 * stdy ** 2.0)
        )
    )
    return z.ravel()


def histogram_gaussian(file_name, binsize_pixels):
    """ Fits 2-D Gaussian to a 2-D histogram from data in .csv file

    Args:
        filename (str): File with (weighted) localization data
        binsize_pixels (int): The size of each bin in the histogram in units px.
    """

    start_time = perf_counter() # Timer for function
    file = pd.read_csv(file_name)  # Read whole file
    x = file["x [nm]"] # Split file into columns
    y = file["y [nm]"]

    bins = int(100/binsize_pixels)
    histogram_vals = np.histogram2d(x, y, bins, normed=False)
    binned_xy = histogram_vals[0]
    # Create histogram data

    bin_centers_x, bin_centers_y = np.arange(0, bins, 1), np.arange(0, bins, 1)
    # Plotting range

    # Curve Fit parameters
    popt, pcov = curve_fit(
        gauss_2d,
        (bin_centers_x, bin_centers_y),
        binned_xy.ravel(),
        p0=[binned_xy.max(),
            np.mean(bin_centers_x), np.mean(bin_centers_y),
            np.std(bin_centers_x), np.std(bin_centers_y)],
        absolute_sigma=True)
    # Generate Gaussian parameters from bins as a tuple for x, and the histogram
    # values as y
    perr = np.sqrt(np.diag(pcov)) # Errors in fit parameters as defined

    mean_fit = (popt[1] + popt[2])/2 # Unpack parameters
    mean_err = perr[0]
    sigma_fit = (popt[3] + popt[4])/2
    sigma_err = perr[1]
    fwhm_fit = 2.355*sigma_fit
    fwhm_err = 2.355*sigma_err

    # Outputting parameters
    print("\n",filename[5:-4],"\n")
    print("\nPixel Values: \nFit mean = ({} ± {})px\nFit std = ({} ± {})px\nFit FWHM = ({} ± {})px"
          .format(mean_fit, mean_err,
                  sigma_fit, sigma_err,
                  fwhm_fit, fwhm_err))
    print("\nNanometer Values: \nFit mean = ({} ± {})nm\nFit std = ({} ± {})nm\nFit FWHM = ({} ± {})nm\n"
          .format(mean_fit*binsize_pixels, mean_err*binsize_pixels,
                  sigma_fit*binsize_pixels, sigma_err*binsize_pixels,
                  fwhm_fit*binsize_pixels, fwhm_err*binsize_pixels))
    end_time = perf_counter() # Time to process localizations and create fit parameters
    time_taken = end_time - start_time
    normalized_time = time_taken / (len(x)/100)
    print("Time taken per 100 localization = {}s".format(normalized_time))

    if PLOT_CHOICE == "N":
        return normalized_time

    else:

        #Plotting and visualisation routines below
        data_fitted = gauss_2d((bin_centers_x, bin_centers_y), *popt) # Fit gaussian

        plt.imshow(binned_xy, cmap=plt.cm.jet, origin="lower")
        plt.colorbar()
        plt.xlabel("x [px]")
        plt.ylabel("y [px]")
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
        ax.contour(bin_centers_x, bin_centers_y,
                   data_fitted.reshape(bins, bins),
                   8, colors="k", linewidths = 0.6)
        mesh = ax.pcolormesh(bin_centers_x, bin_centers_y,
                             data_fitted.reshape(bins,bins))
        fig.colorbar(mesh)
        ax.set_xlabel("x [px]")
        ax.set_ylabel("y [px]")
        plt.show()

        X, Y = np.meshgrid(bin_centers_x, bin_centers_y)

        fig = plt.figure()
        ax = plt.axes(projection='3d')
        ax.plot_surface(X, Y, data_fitted.reshape(bins,bins),
                        cmap = 'viridis', edgecolors = 'k', lw = 0.6)
        ax.set_xlabel("x [px]")
        ax.set_ylabel("y [px]")
        ax.set_zlabel("Count")
        plt.show()
        return normalized_time

# User inputting routine that performs above
filename = askopenfilename(
    title="Open File (csv of with 'x [nm]' and 'y [nm]' columns)",
    filetypes=[('Comma Separated Values File','*.csv')]
    )
binsize = int(input("Please enter desired bin size in pixels: "))
PLOT_CHOICE = str(input("Would you like visualisation? Y/N: "))
histogram_gaussian(filename, binsize)
