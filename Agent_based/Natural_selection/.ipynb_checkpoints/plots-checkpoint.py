import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from tqdm import tqdm
from matplotlib.animation import FuncAnimation 
from IPython.display import HTML
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

plt.rc('text', usetex=True)
plt.rc('font', family='serif')

plt.rcParams['figure.dpi'] = 100

import sys
sys.path.append("/home/pedroc/git-projects/pasta-marker")

from pastamarkers import markers

from svgpathtools import svg2paths
from svgpath2mpl import parse_path

ant_path, attributes = svg2paths('/home/pedroc/Documentos/pedro/Theoretical_ecology/ant.svg')

ant_marker = parse_path(attributes[0]['d'])
ant_marker.vertices -= ant_marker.vertices.mean(axis=0)
ant_marker = ant_marker.transformed(mpl.transforms.Affine2D().rotate_deg(270))
ant_marker = ant_marker.transformed(mpl.transforms.Affine2D().scale(-1,1))

def getImage(path):
    return OffsetImage(plt.imread(path, format="png"), zoom=0.05)

img_path = '/home/pedroc/Documentos/pedro/Theoretical_ecology/Pacoca-doce.png'

def plot(fig, ax, frame, L, positions, velocities, food_pos, life, food_population, population, nsteps, sight_vec, mean_sight_vec, mean_vel_vec, plot_frequency, save = True, show = False):
    for x in range(len(ax)):
        ax[x].clear()
        
    for i in range(len(positions[frame])):
        if life[frame][i] == 1:
            color = 'navy'
        # elif life[frame][i] == 0:
        #     color = 'firebrick'
            
        # t = mpl.markers.MarkerStyle(marker = ant_marker)
        # t._transform = t.get_transform().rotate_deg(180*angles[frame][i]/np.pi)
        # ax[0].scatter(positions[frame][i][0], positions[frame][i][1], marker = t, s = 300, lw = 0,
        #              facecolor = color)
            ax[0].scatter(positions[frame][i][0], positions[frame][i][1], s = 50, lw = 0,
                         facecolor = color)
        # circle = plt.Circle((positions[frame][i][0], positions[frame][i][1]), sight_radius, edgecolor='grey',
        #                    facecolor = 'none')
        # if life[frame][i] == 1:
        #     ax[0].add_patch(circle)
        # ax[0].quiver(positions[frame][0], positions[frame][1],
        #            v*np.cos(angles[frame]), v*np.sin(angles[frame]), zorder = 0,
        #             scale = 15, width = 0.007, color = 'crimson')
        # ax[0].scatter(food_pos[frame][:,0], food_pos[frame][:,1], marker = markers.farfalle, s = 400,
        #               lw = 0.5, edgecolor = 'black')

    ax[0].scatter(food_pos[frame][:,0], food_pos[frame][:,1], marker = markers.farfalle, s = 400,
                      lw = 0.5, edgecolor = 'black')
    # for f in food_pos[frame]:
    #     ab = AnnotationBbox(getImage(img_path), (f[0], f[1]), frameon=False)
    #     ax[0].add_artist(ab)

    ax[0].set_xlim(0, L)
    ax[0].set_ylim(0, L)

    ax[0].set_xticks([])
    ax[0].set_yticks([])
    
#     ax[1].set_xlim(0, 2)
#     ax[1].set_ylim(0, max_energy)
#     for i in range(len(positions)):
#         ax[1].bar(i, energy[i,frame], width = 1,
#                   color = sns.color_palette('Spectral', int(max_energy+1))[int(energy[i,frame])],
#                  align = 'edge', edgecolor = 'black')
    
#     ax[1].set_xticks([])
#     ax[1].yaxis.tick_right()
#     ax[1].set_yticks([0, max_energy/4, max_energy/2, 3*max_energy/4, max_energy])
#     ax[1].set_yticklabels(["0\%", "25\%", "50\%", "75\%", "100\%"], fontsize = 12)
    
    ax[1].yaxis.tick_right()
    ax[1].yaxis.set_label_position("right")
    ax[1].plot([j for j in range(frame)], food_population[:frame], lw = 2, color = 'black')
    ax[1].scatter(frame, food_population[frame], s = 40, color = 'black')
    
    ax[1].plot([j for j in range(frame)], population[:frame], lw = 2, color = 'navy')
    ax[1].scatter(frame, population[frame], s = 40, color = 'navy')
    
    # ab = AnnotationBbox(getImage(img_path), (frame, food_population[frame]), frameon=False)
    # ax[1].add_artist(ab)
    ax[1].set_xlim(0, nsteps)
    ax[1].set_ylim(0, 120)
    ax[1].set_xticks([200*i for i in range(nsteps//200 + 1)])
    ax[1].set_xticklabels([200*i for i in range(nsteps//200 + 1)], fontsize = 12)
    ax[1].set_yticks([0,20,40,60,80,100,120])
    ax[1].set_yticklabels([0,20,40,60,80,100,120], fontsize = 12)
    ax[1].set_xlabel("Tempo", fontsize = 16, labelpad = 10)
    ax[1].set_ylabel("População", fontsize = 16, labelpad = 10)
    # ax[1].scatter(frame, food_population[j])
    
    if len(ax) == 4:
        values, bins = np.histogram(sight_vec[frame], bins = [0.5*i for i in range(17)], density = True)

        for b in range(len(values)):
            ax[2].bar(bins[b], values[b], align = 'edge', edgecolor = 'black', width = 0.5,
                       facecolor = sns.color_palette("magma", 17)[b])

        ax[2].set_xlim(0, 8)
        ax[2].set_ylim(0, 1)
        ax[2].set_xlabel("Raio de percepção", fontsize = 16, labelpad = 10)
        ax[2].set_yticks([])
        ax[2].spines[['top','right']].set_visible(False)
        ax[2].set_xticks([i for i in range(9)])
        ax[2].set_xticklabels([i for i in range(9)], fontsize = 12)

        ax[3].yaxis.tick_right()
        ax[3].yaxis.set_label_position("right")
        ax[3].axhline(mean_sight_vec[0], lw = 1, ls = '--', color = 'grey', alpha = 0.6)
        ax[3].plot([j for j in range(frame+1)], mean_sight_vec, lw = 2, color = 'black')
        ax[3].scatter(frame, mean_sight_vec[frame], s = 40, color = 'black')
        ax[3].set_xlim(0, nsteps)
        ax[3].set_ylim(1, 3)
        ax[3].set_xticks([200*i for i in range(nsteps//200 + 1)])
        ax[3].set_xticklabels([200*i for i in range(nsteps//200 + 1)], fontsize = 12)
        ax[3].set_yticks([0.5*i for i in range(2,7)])
        ax[3].set_yticklabels([f"{0.5*i:.1f}" for i in range(2,7)], fontsize = 12)
        ax[3].set_xlabel("Tempo", fontsize = 16, labelpad = 10)
        ax[3].set_ylabel("Raio de percepção médio", fontsize = 16, labelpad = 10)
    
    elif len(ax) == 6:
        values, bins = np.histogram(velocities[frame], bins = [0.2*i for i in range(26)], density = True)

        for b in range(len(values)):
            ax[4].bar(bins[b], values[b], align = 'edge', edgecolor = 'black', width = 0.2,
                       facecolor = sns.color_palette("magma", 26)[b])

        ax[4].set_xlim(0, 5)
        ax[4].set_ylim(0, 1.5)
        ax[4].set_xlabel("Velocidade", fontsize = 16, labelpad = 10)
        ax[4].set_yticks([])
        ax[4].spines[['top','right']].set_visible(False)
        ax[4].set_xticks([i for i in range(6)])
        ax[4].set_xticklabels([f"{i}" for i in range(6)], fontsize = 12)

        ax[5].yaxis.tick_right()
        ax[5].yaxis.set_label_position("right")
        ax[5].axhline(mean_vel_vec[0], lw = 1, ls = '--', color = 'grey', alpha = 0.6)
        ax[5].plot([j for j in range(frame+1)], mean_vel_vec, lw = 2, color = 'black')
        ax[5].scatter(frame, mean_vel_vec[frame], s = 40, color = 'black')
        ax[5].set_xlim(0, nsteps)
        ax[5].set_ylim(0, 2)
        ax[5].set_xticks([200*i for i in range(nsteps//200 + 1)])
        ax[5].set_xticklabels([200*i for i in range(nsteps//200 + 1)], fontsize = 12)
        ax[5].set_yticks([0.5*i for i in range(5)])
        ax[5].set_yticklabels([f"{0.5*i:.1f}" for i in range(5)], fontsize = 12)
        ax[5].set_xlabel("Tempo", fontsize = 16, labelpad = 10)
        ax[5].set_ylabel("Velocidade média", fontsize = 16, labelpad = 10)
    
    plt.tight_layout()
    
    if save:
        plt.savefig(f"Gifs/Frames/frame_{frame//plot_frequency}.png", dpi = 90, bbox_inches = 'tight')
    if show:
        plt.show()
    else:
        plt.close()
        
def imshow3d(ax, array, value_direction='z', pos=0, norm=None, cmap=None):
    """
    Display a 2D array as a  color-coded 2D image embedded in 3d.

    The image will be in a plane perpendicular to the coordinate axis *value_direction*.

    Parameters
    ----------
    ax : Axes3D
        The 3D Axes to plot into.
    array : 2D numpy array
        The image values.
    value_direction : {'x', 'y', 'z'}
        The axis normal to the image plane.
    pos : float
        The numeric value on the *value_direction* axis at which the image plane is
        located.
    norm : `~matplotlib.colors.Normalize`, default: Normalize
        The normalization method used to scale scalar data. See `imshow()`.
    cmap : str or `~matplotlib.colors.Colormap`, default: :rc:`image.cmap`
        The Colormap instance or registered colormap name used to map scalar data
        to colors.
    """
    if norm is None:
        norm = Normalize()
    colors = plt.get_cmap(cmap)(norm(array))

    if value_direction == 'x':
        nz, ny = array.shape
        zi, yi = np.mgrid[0:nz + 1, 0:ny + 1]
        xi = np.full_like(yi, pos)
    elif value_direction == 'y':
        nx, nz = array.shape
        xi, zi = np.mgrid[0:nx + 1, 0:nz + 1]
        yi = np.full_like(zi, pos)
    elif value_direction == 'z':
        ny, nx = array.shape
        yi, xi = np.mgrid[0:ny + 1, 0:nx + 1]
        zi = np.full_like(xi, pos)
    else:
        raise ValueError(f"Invalid value_direction: {value_direction!r}")
    ax.plot_surface(xi, yi, zi, rstride=1, cstride=1, facecolors=colors, shade=False)