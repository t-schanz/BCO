from BCO.Instruments import Radar,Windlidar
from BCO.tools.tools import time2num,num2time
from datetime import datetime as dt
from datetime import timedelta
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage
from scipy.ndimage.morphology import binary_erosion

def getStartEnd():
    date = dt.today() - timedelta(days=2)
    start = dt(date.year,date.month,date.day,0,0,0)
    end = dt(date.year,date.month,date.day,23,59,59)

    return start,end

def countClouds(radarVel):
    radarVel[np.isnan(radarVel)] = -999
    mask = radarVel >  -998
    structure_array = np.ones([3,3])
    label_im, nb_labels = ndimage.label(mask, structure=structure_array)
    print("Clouds in picture: %i" %nb_labels)
    label_im = label_im.astype(float)
    label_im[label_im == -999] = np.nan
    # plt.contourf(label_im.transpose())
    return label_im, nb_labels

def cloudShapes(im):
    im[np.where(im != 0)] = 1

    im1 = binary_erosion(im,iterations=2)

    im = np.subtract(im,im1)

    im[np.where(im == 0)] = np.nan

    im[0,0] = -9999

    return im




if __name__ == "__main__":

    # ================================
    # Load Data:
    # ================================

    start,end = getStartEnd()
    coral = Radar(start,end,version=2)
    lidar = Windlidar(start,end)

    coralTime = coral.getTime()
    lidarTime = lidar.getTime()

    coralRange = coral.getRange()
    lidarRange = lidar.getRange()

    coralVel = coral.getVelocity()
    lidarVel = lidar.getVelocity()




    # =================================
    # Plotting:
    # =================================

    fig,(ax0,ax1,ax2,ax3,ax4) = plt.subplots(nrows=5,ncols=1,figsize=(16,9))

    # ax.contourf(lidarTime,lidarRange,lidarVel.transpose())
    # ax.contourf(coralTime,coralRange,coralVel.transpose())

    label_im,nb_labels = countClouds(coralVel.copy())

    label_im = cloudShapes(label_im)




    ax0.set_ylim(0,2000)
    ax0.contourf(lidarTime,lidarRange,lidarVel.transpose(),cmap="Spectral_r")
    ax0.contourf(coralTime,coralRange,coralVel.transpose(),cmap="Spectral_r")
    ax0.contourf(coralTime,coralRange,label_im.transpose(), cmap="binary")

    axes = [ax1,ax2,ax3,ax4]
    timesteps = [int((len(coralTime)/4)*i) for i in range(5)]
    timesteps[-1] -= 1
    timetups = [(timesteps[i],timesteps[i+1]) for i in range(4)]
    for ax,step in zip(axes,timetups):
        print(step)
        ax.set_ylim(0,2000)
        ax.set_xlim(coralTime[step[0]],coralTime[step[1]])
        ax.contourf(lidarTime, lidarRange, lidarVel.transpose(), cmap="Spectral_r")
        ax.contourf(coralTime, coralRange, coralVel.transpose(), cmap="Spectral_r")
        ax.contourf(coralTime, coralRange, label_im.transpose(), cmap="binary")

    plt.savefig("Velocities.png")








