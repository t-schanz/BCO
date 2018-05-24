"""
Module for plotting a combined vertical velocities plot. Inside clouds data from the Radar is being used.
Outside the clouds, the data comes from the lidar.

Usage:
    >>> python3 RadarLidarVelocies.py YYYYMMDD

        where YYYYMMDD is the date, e.g.: 20180130 would be the 30th of January in 2018.

    If no date is provided, the day before the actual system time will be used (usually yesterday).

"""
import sys
sys.path.insert(0,"/home/mpim/m300517/MPI/working/BCO")

from BCO.Instruments import Radar,Windlidar
from BCO.tools.convert import num2time, time2num
from datetime import datetime as dt
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from scipy import ndimage
from scipy.ndimage.morphology import binary_erosion
import warnings




def getStartEnd(datestr):
    """
    Determine the start and end values for this script.

    Returns:
        start: datetime.datetime-obj
        end: datetime.datetime-obj
    """

    if datestr:
        date = dt.strptime(datestr,"%Y%m%d")

    else:
        date = dt.today() - timedelta(days=1)

    start = dt(date.year,date.month,date.day,0,0,0).strftime("%Y%m%d")
    end = dt(date.year,date.month,date.day,23,59,59).strftime("%Y%m%d")

    return start,end

def countClouds(radarVel):
    """
    Function to label all values belonging to one cloud with the same number.

    Args:
        radarVel: np.array of the radar Velocities or Reflection

    Returns:
        np.array where each cloud now is a cluster of the same number. Each cloud gets a new number.
    """

    radarVel[np.isnan(radarVel)] = -999
    mask = radarVel >  -998
    structure_array = np.ones([3,3])
    label_im, nb_labels = ndimage.label(mask, structure=structure_array)
    print("Clouds in picture: %i" %nb_labels)
    label_im = label_im.astype(float)
    label_im[label_im == -999] = np.nan
    return label_im, nb_labels

def cloudShapes(im):
    """
    Function to get the Contours of clouds from Radar Data.

    Args:
        im: Array where clouds have only one value (return of countClouds)

    Returns:
        np.array where the contours of clouds are marked as 1, the rest is set to np.nan. The value [0,0] of the array
        is set to -9999 for the right coloring later.
    """
    im[np.where(im != 0)] = 1

    im1 = binary_erosion(im,iterations=2)

    im = np.subtract(im,im1)

    im[np.where(im == 0)] = np.nan

    im[0,0] = -9999

    return im

def rainRate(ref):
    """
    Rain rate calculated with Mashall-Palmer Relationship

    Args:
        ref: Radar reflectivity

    Returns: Array with rain intensities

    """
    return np.multiply(0.036,np.power(10,np.multiply(0.0625,ref)))

def getRainmask(vel,ref):
    mask = np.asarray(ref.copy())
    mask[np.less(mask,999999)] = np.nan #setting whole mask to nan
    rain = rainRate(ref.copy())
    mask[np.logical_and(np.less(vel,-1),np.greater_equal(rain,0.1))] = 1

    mask[0,0] = -9999
    return mask

def noDataMask(lidarVel):
    mask = np.asarray(lidarVel.copy())
    mask[np.less(mask,999999)] = np.nan #setting whole mask to nan
    mask[np.isnan(lidarVel)] = 1
    mask[0,0] = -9999
    return mask

def get_xlims(time):
    start_date = dt(time.year,time.month,time.day,0,0,0)
    dates = []
    for n in range(0,25,6):
        dates.append( start_date + timedelta(hours=n))
    return dates


def plotData(lidarTime,lidarRange,lidarVel,coralTime,coralRange,coralVel,coralRef,threshold,datestr,save_path=""):
    """
    Function for actually creating the plot.

    """
    # Set up custom Colormap:

    colorlist = ["#ffffff","#D3D3D3"]
    cm_name = "anyName"

    cm = LinearSegmentedColormap.from_list(cm_name,colorlist,2)


    font_size = 16
    colors = "bwr"

    fig,(ax1,ax2,ax3,ax4) = plt.subplots(nrows=4,ncols=1,figsize=(16,9))
    fig.suptitle("%s, Vertical Velocities from Radar and Lidar"%(lidarTime[0].strftime("%d.%m.%Y")), fontsize=20)

    hourlocators = [mdates.HourLocator() for _ in range(4)]
    time_fmts = [mdates.DateFormatter("%H:00") for i in range(4)]


    rain_patch = mpatches.Patch(facecolor="lightgrey",alpha=0.91, label='Precipitation')
    noData_patch = mpatches.Patch(color='dimgrey', label='Out of Lidar Range')

    label_im,nb_labels = countClouds(coralVel.copy())
    label_im = cloudShapes(label_im.copy())
    rainmask = getRainmask(coralVel.copy(),coralRef.copy())
    noData = noDataMask(lidarVel.copy())

    axes = [ax1,ax2,ax3,ax4]
    timesteps = get_xlims(coralTime[10])
    timetups = [(timesteps[i],timesteps[i+1]) for i in range(4)]

    ax1.legend(handles=[rain_patch, noData_patch], bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.,fontsize=font_size)
    for ax,step,hourlocator,time_fmt in zip(axes,timetups,hourlocators,time_fmts):
        # print(step)
        ax.set_ylim(0,1500)
        ax.set_xlim(step[0],step[1])
        ax.contourf(lidarTime, lidarRange, lidarVel.transpose(), cmap=colors) # Lidar Data
        ax.contourf(lidarTime,lidarRange,noData.transpose(),cmap="Accent") # Above Lidar Range
        im = ax.contourf(coralTime, coralRange, coralVel.transpose(), cmap=colors) # Rada Data

        # ax.contourf(coralTime,coralRange,rainmask.transpose(),colors='none',hatches=["///"]) # Mask for Rain
        ax.contourf(coralTime, coralRange, label_im.transpose(), cmap="binary") # Mask for cloud contours

        ax.fill_between(coralTime,0,1500,where=np.nansum(rainmask[:,:44], axis=1) > 0 , facecolor="lightgrey", alpha=0.91)

        ax.xaxis.set_major_locator(hourlocator)
        ax.xaxis.set_major_formatter(time_fmt)

        ax.tick_params(labelsize=font_size)

        ax.set_ylabel("Height [m]",fontsize=font_size)

    ax.set_xlabel("Time [UTC]",fontsize=font_size) # set xlabel just on the last plot

    plt.tight_layout()

    fig.subplots_adjust(right=0.8,top=0.92)
    cbar_ax = fig.add_axes([0.85,0.15,0.02,0.6])

    norm = mpl.colors.Normalize(vmin=-threshold,vmax=threshold)
    cb = mpl.colorbar.ColorbarBase(cbar_ax,cmap=colors,norm=norm,orientation="vertical",extend="both")
    cb.ax.tick_params(labelsize=font_size)
    cb.set_label("Vertical Velocity [m$\,$s$^{-1}$]",fontsize=font_size)

    plt.savefig(save_path + "Velocities_%s.png"%datestr)

def roundLidarVel(lidarTime,lidarVel,lidarInt):
    """
    Function to lower the amount of data used. The lidar has a temporal resolution of about 1s. Plotting all this data
    takes ages and does not bring any more information in this case than a 10s resolution data. Therefore this function
    smallers the original temporal resolution by a factor 7.

    Args:
        lidarTime: np.array of the timesteps of the lidar
        lidarVel: np.array of the Velocities of the lidar
        lidarInt: np.array of the Intensities of the backscatterering function of the Lidar

    Returns:
        All inputs reduced in size by a factor 7.

    """
    lidarTimeNew = np.asarray(lidarTime[::7])
    lidarVelNew = np.asarray(lidarVel[::7,:])
    lidarIntNew = np.asarray(lidarInt[::7,:])
    return lidarTimeNew,lidarVelNew,lidarIntNew


def filterWindLidar(lidarVel,lidarInt,windFilter=-18.3):
    """
    Function to filter out the noise of the Windlidar (copied from Aude Untersee (MPI))

    Args:
        lidarVel: np.array of the Velocities of the lidar
        lidarInt: np.array of the Intensities of the backscatterering function of the Lidar
        windFilter: The Filter-value in dBZ

    Returns:
        lidarVelFiltered: np.array of the filtered Velocities

    """
    SNR = np.subtract(lidarInt,1)
    SNR_dB = np.multiply(10,np.log10(SNR)) #SNR in dBz
    lidarVelFiltered = np.where(np.less_equal(SNR_dB,windFilter),np.nan,lidarVel)
    return lidarVelFiltered


def plot_RadarLidarVelcities(datestr=None, output_path=""):
    """
    Creates an image with the combined vertical velocities from Radar and Windlidar.
    The image is created for the day defined by the datestr-argument.
    If no datestr is provided the plot will be created for yesterdays data.


    Args:
        datestr: Format: YYYYMMDD

    Returns:
        Saves an image in the defined output_path.

    Example:

        >>> from BCO.Quicklooks import plot_RadarLidarVelcities
        >>> plot_RadarLidarVelcities("20170723")

    .. image:: ../_images/Velocities_20170723.png
        :width: 400px
        :align: center
        :height: 200px
        :alt: alternate text
    """
    warnings.filterwarnings("ignore") # for debugging comment this line!!!

    save_path = output_path # path where image will be saved.


    # ================================
    # Load Data:
    # ================================


    start,end = getStartEnd(datestr)


    coral = Radar(start,end,version=2)
    lidar = Windlidar(start,end)


    coralTime = coral.getTime()
    lidarTime = lidar.getTime()

    coralRange = coral.getRange()
    lidarRange = lidar.getRange()

    coralVel = coral.getVelocity()
    lidarVel = lidar.getVelocity()
    lidarVel[:,:2] = np.nan



    lidarInt = lidar.getIntensity()
    coralRef = coral.getReflectivity()


    # ================================
    # Adjusting Data for Plotting:
    # ================================

    lidarTime,lidarVel,lidarInt = roundLidarVel(lidarTime,lidarVel,lidarInt) # make the timeresolution ca. 10s
    lidarVel = filterWindLidar(lidarVel,lidarInt)

    coralRef[np.less(coralRef, -50)] = np.nan  # Filter all values smaller than -50 dbZ
    coralVel[np.isnan(coralRef)] = np.nan # Applying the same filter to the Velocities

    lidarVel[:, 33:][np.greater_equal(abs(lidarVel[:, 33:]), 3)] = np.nan  # removes noise above 1km

    #Setting everything above the threshold to threshold, to make smaller values visible

    threshold = 2
    lidarVel[np.greater(lidarVel,threshold)] = threshold
    coralVel[np.greater(coralVel,threshold)] = threshold
    lidarVel[np.less(lidarVel,-threshold)] = -threshold
    coralVel[np.less(coralVel,-threshold)] = -threshold




    # =================================
    # Plotting:
    # =================================

    plotData(lidarTime,lidarRange,lidarVel,coralTime,coralRange,coralVel,coralRef,threshold,start,save_path)


if __name__ == "__main__":
    # ================================
    # Get Parameters:
    # ================================

    try:
        datestr = sys.argv[1]
    except:
        datestr = None

    save_path = ""

    # ================================
    # Start program:
    # ================================
    plot_RadarLidarVelcities(datestr,save_path)
