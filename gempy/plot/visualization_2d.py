"""
    This file is part of gempy.

    gempy is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    gempy is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with gempy.  If not, see <http://www.gnu.org/licenses/>.


Module with classes and methods to visualized structural geology data and potential fields of the regional modelling based on
the potential field method.
Tested on Ubuntu 14

Created on 23/09/2016

@author: Miguel de la Varga
"""

import warnings
import os


import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import numpy as np
from os import path
import sys
# This is for sphenix to find the packages
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from gempy.core.solution import Solution

sns.set_context('talk')
plt.style.use(['seaborn-white', 'seaborn-talk'])


class PlotData2D(object):
    """
    Class to make the different plot related with gempy

    Args:
        geo_data(gempy.InputData): All values of a DataManagement object
        block(numpy.array): 3D array containing the lithology block
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        scalar_field(numpy.ndarray): 3D array containing a individual potential field
        verbose(int): Level of verbosity during the execution of the functions (up to 5). Default 0
    """

    def __init__(self, model, **kwargs):

        self.model = model

        self._color_lot = dict(zip(self.model.surfaces.df['surface'], self.model.surfaces.df['color'])) # model.surfaces.colors.colordict
        self._cmap = mcolors.ListedColormap(list(self.model.surfaces.df['color']))
        self._norm = mcolors.Normalize(vmin=0.5, vmax=len(self._cmap.colors)+0.5)

        self._set_style()

    @staticmethod
    def _set_style():
        """
        Private function to set some plot options

        """

        plt.style.use(['seaborn-white', 'seaborn-talk'])
        sns.set_context("talk")

    def plot_data(self, direction="y", data_type='all', series="all", legend_font_size=10, ve=1, **kwargs):
        """
        Plot the projecton of the raw data (surface_points and orientations) in 2D following a
        specific directions

        Args:
            direction(str): xyz. Caartesian direction to be plotted
            data_type (str): type of data to plot. 'all', 'surface_points' or 'orientations'
            series(str): series to plot
            ve(float): Vertical exageration
            **kwargs: seaborn lmplot key arguments. (TODO: adding the link to them)

        Returns:
            Data plot

        """
        if 'scatter_kws' not in kwargs:
            kwargs['scatter_kws'] = {"marker": "D",
                                     "s": 100,
                                     "edgecolors": "black",
                                     "linewidths": 1}

        x, y, Gx, Gy = self._slice(direction)[4:]
        extent = self._slice(direction)[3]
        aspect = (extent[1] - extent[0])/(extent[3] - extent[2])

        # apply vertical exageration
        if direction == 'x' or direction == 'y':
            aspect /= ve

        if aspect < 1:
            min_axis = 'width'
        else:
            min_axis = 'height'

        if series == "all":
            series_to_plot_i = self.model.surface_points.df[self.model.surface_points.df["series"].
                isin(self.model.series.df.index.values)]
            series_to_plot_f = self.model.orientations.df[self.model.orientations.df["series"].
                isin(self.model.series.df.index.values)]

        else:

            series_to_plot_i = self.model.surface_points[self.model.surface_points.df["series"] == series]
            series_to_plot_f = self.model.orientations[self.model.orientations.df["series"] == series]

        #fig, ax = plt.subplots()

    #    series_to_plot_i['surface'] = series_to_plot_i['surface'].cat.remove_unused_categories()
    #    series_to_plot_f['surface'] = series_to_plot_f['surface'].cat.remove_unused_categories()
        #print(self._color_lot)
        if data_type == 'all':
            p = sns.lmplot(x, y,
                           data=series_to_plot_i,
                           fit_reg=False,
                           aspect=aspect,
                           hue="surface",
                           #scatter_kws=scatter_kws,
                           legend=False,
                           legend_out=False,
                           palette= self._color_lot,#np.asarray([tuple(i) for i in self._color_lot.values()]),
                           **kwargs)

            p.axes[0, 0].set_ylim(extent[2], extent[3])
            p.axes[0, 0].set_xlim(extent[0], extent[1])

            # Plotting orientations
            plt.quiver(series_to_plot_f[x], series_to_plot_f[y],
                       series_to_plot_f[Gx], series_to_plot_f[Gy],
                       pivot="tail", scale_units=min_axis, scale=10)

        if data_type == 'surface_points':
            p = sns.lmplot(x, y,
                           data=series_to_plot_i,
                           fit_reg=False,
                           aspect=aspect,
                           hue="surface",
                           #scatter_kws=scatter_kws,
                           legend=False,
                           legend_out=False,
                           palette=self._color_lot,
                           **kwargs)
            p.axes[0, 0].set_ylim(extent[2], extent[3])
            p.axes[0, 0].set_xlim(extent[0], extent[1])


        if data_type == 'orientations':
            plt.quiver(series_to_plot_f[x], series_to_plot_f[y],
                       series_to_plot_f[Gx], series_to_plot_f[Gy],
                       pivot="tail", scale_units=min_axis, scale=15)



        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

        # plt.xlim(extent[0] - extent[0]*0.05, extent[1] + extent[1]*0.05)
        # plt.ylim(extent[2] - extent[2]*0.05, extent[3] + extent[3]*0.05)
        plt.xlabel(x)
        plt.ylabel(y)

        #return fig, ax, p

    def _slice(self, direction, cell_number=25):
        """
        Slice the 3D array (blocks or scalar field) in the specific direction selected in the plot functions

        """
        _a, _b, _c = (slice(0, self.model.grid.resolution[0]),
                      slice(0, self.model.grid.resolution[1]),
                      slice(0, self.model.grid.resolution[2]))
        if direction == "x":
            _a = cell_number
            x = "Y"
            y = "Z"
            Gx = "G_y"
            Gy = "G_z"
            extent_val = self.model.grid.extent[[2,3,4,5]]
        elif direction == "y":
            _b = cell_number
            x = "X"
            y = "Z"
            Gx = "G_x"
            Gy = "G_z"
            extent_val = self.model.grid.extent[[0, 1, 4, 5]]
        elif direction == "z":
            _c = cell_number
            x = "X"
            y = "Y"
            Gx = "G_x"
            Gy = "G_y"
            extent_val = self.model.grid.extent[[1, 2, 3, 4]]
        else:
            raise AttributeError(str(direction) + "must be a cartesian direction, i.e. xyz")
        return _a, _b, _c, extent_val, x, y, Gx, Gy

    def _slice2D(self, cell_number, direction):
        if direction == 'x':
            _slice = np.s_[cell_number, :, :]
            extent = self.model.grid.extent[[2, 3, 4, 5]]
        elif direction == 'y':
            _slice = np.s_[:, cell_number, :]
            extent = self.model.grid.extent[[0, 1, 4, 5]]
        elif direction == 'z':
            _slice = np.s_[:, :, cell_number]
            extent = self.model.grid.extent[[1, 2, 3, 4]]
        else:
            print('not a direction')
        return _slice, extent

    def plot_topography(self, cell_number, direction):
        line = self.model.topography._line_in_section(cell_number=cell_number, direction=direction)
        if direction == 'x':
            ext = self.model.grid.extent[[2, 3, 4, 5]]
        elif direction == 'y':
            ext = self.model.grid.extent[[0, 1, 4, 5]]
        # add corners
        line = np.append(line, ([ext[1], line[0, -1]], [ext[1], ext[3]], [ext[0], ext[3]], [ext[0], line[0, 1]])).reshape(-1,2)
        plt.fill(line[:, 0], line[:, 1], color='k', alpha=0.5)


    def extract_fault_lines(self, cell_number=25, direction='y'):

        faults = list(self.model.faults.faults_relations_df.form_series[
                          self.model.faults.faults_relations_df.form_series == True].index)
        _slice, extent = self._slice2D(cell_number, direction)

        for fault in faults:
            f_id = int(self.model.series.df.loc[fault, 'order_series']) - 1
            block = self.model.solutions.scalar_field_matrix[f_id]
            level = self.model.solutions.scalar_field_at_surface_points[f_id][np.where(
                self.model.solutions.scalar_field_at_surface_points[f_id] != 0)]
            plt.contour(block.reshape(self.model.grid.resolution)[_slice].T, 0, extent=extent, levels=level,
                        colors=self._cmap.colors[f_id])

    def plot_block_section(self, solution:Solution, cell_number=13, block=None, direction="y", interpolation='none',
                           plot_data=False, block_type='lithology', ve=1, show_faults=False, show_topo = True, **kwargs):
        """
        Plot a section of the block model

        Args:
            cell_number(int): position of the array to plot
            direction(str): xyz. Caartesian direction to be plotted
            interpolation(str): Type of interpolation of plt.imshow. Default 'none'.  Acceptable values are 'none'
            ,'nearest', 'bilinear', 'bicubic',
            'spline16', 'spline36', 'hanning', 'hamming', 'hermite', 'kaiser',
            'quadric', 'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc',
            'lanczos'
            ve(float): Vertical exageration
            **kwargs: imshow keywargs

        Returns:
            Block plot
        """

        if type(block) is not str:
            warnings.warn('Passing the block directly will get deprecated in the next version. Please use Solution'
                          'and block_type instead', FutureWarning)
            _block = block
        else:
            if block_type is 'lithology':
                _block = solution.lith_block

            elif block_type is 'fault1':
                _block = solution.fault_blocks

            else:
                assert block_type in self.model.surfaces.df.columns, 'The value to be plotted has to be in surfaces: \\' + \
                                                                   str(self.model.surfaces.df)

        plot_block = _block.reshape(self.model.grid.resolution[0], self.model.grid.resolution[1], self.model.grid.resolution[2])
        _a, _b, _c, extent_val, x, y = self._slice(direction, cell_number)[:-2]

        if plot_data:
            self.plot_data(direction, 'all')
        # TODO: plot_topo option - need fault_block for that

        # apply vertical exageration
        if direction == 'x' or direction == 'y':
            aspect = ve
        else:
            aspect = 1

        if 'cmap' not in kwargs:
            kwargs['cmap'] = self._cmap
        if 'norm' not in kwargs:
            kwargs['norm'] = self._norm

        im = plt.imshow(plot_block[_a, _b, _c].T, origin="bottom",
                        extent=extent_val,
                        interpolation=interpolation,
                        aspect=aspect,
                        **kwargs)
        if show_faults:
            #raise NotImplementedError
            self.extract_fault_lines(cell_number, direction)

        if show_topo:
            if self.model.topography is not None:
                self.plot_topography(cell_number=cell_number, direction=direction)

        if not plot_data:
            import matplotlib.patches as mpatches
            patches = [mpatches.Patch(color=color, label=surface) for surface, color in self._color_lot.items()]
            plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

        plt.xlabel(x)
        plt.ylabel(y)
        return plt.gcf()

    def plot_scalar_field(self, solution, cell_number, series=0, N=20,
                          direction="y", plot_data=True, *args, **kwargs):
        """
        Plot a scalar field in a given direction.

        Args:
            cell_number(int): position of the array to plot
            scalar_field(str): name of the scalar field (or series) to plot
            n_pf(int): number of the  scalar field (or series) to plot
            direction(str): xyz. Caartesian direction to be plotted
            serie: *Deprecated*
            **kwargs: plt.contour kwargs

        Returns:
            scalar field plot
        """

        if isinstance(solution, Solution):
            scalar_field = solution.scalar_field_matrix[series]
        else:
            warnings.warn('Passing the block directly will get deprecated in the next version. Please use Solution'
                          'and block_type instead', FutureWarning)
            scalar_field = solution

        if 'cmap' not in kwargs:
            kwargs['cmap'] = 'magma'

        if plot_data:
            self.plot_data(direction, 'all')

        _a, _b, _c, extent_val, x, y = self._slice(direction, cell_number)[:-2]

        plt.contour(scalar_field.reshape(
            self.model.grid.resolution[0], self.model.grid.resolution[1], self.model.grid.resolution[2])[_a, _b, _c].T,
                    N,
                    extent=extent_val, *args,
                    **kwargs)

        plt.contourf(scalar_field.reshape(
            self.model.grid.resolution[0], self.model.grid.resolution[1], self.model.grid.resolution[2])[_a, _b, _c].T,
                    N,
                    extent=extent_val, alpha=0.6, *args,
                    **kwargs)

        if 'colorbar' in kwargs:
            plt.colorbar()

        plt.xlabel(x)
        plt.ylabel(y)

    @staticmethod
    def plot_topo_g(geo_data, G, centroids, direction="y", label_kwargs=None, node_kwargs=None, edge_kwargs=None):
        if direction == "y":
            c1, c2 = (0, 2)
            e1 = geo_data.grid.extent[1] - geo_data.grid.extent[0]
            e2 = geo_data.grid.extent[5] - geo_data.grid.extent[4]
            d1 = geo_data.grid.extent[0]
            d2 = geo_data.grid.extent[4]
            if len(list(centroids.items())[0][1]) == 2:
                c1, c2 = (0, 1)
            r1 = geo_data.grid.resolution[0]
            r2 = geo_data.grid.resolution[2]
        elif direction == "x":
            c1, c2 = (1, 2)
            e1 = geo_data.grid.extent[3] - geo_data.grid.extent[2]
            e2 = geo_data.grid.extent[5] - geo_data.grid.extent[4]
            d1 = geo_data.grid.extent[2]
            d2 = geo_data.grid.extent[4]
            if len(list(centroids.items())[0][1]) == 2:
                c1, c2 = (0, 1)
            r1 = geo_data.grid.resolution[1]
            r2 = geo_data.grid.resolution[2]
        elif direction == "z":
            c1, c2 = (0, 1)
            e1 = geo_data.grid.extent[1] - geo_data.grid.extent[0]
            e2 = geo_data.grid.extent[3] - geo_data.grid.extent[2]
            d1 = geo_data.grid.extent[0]
            d2 = geo_data.grid.extent[2]
            if len(list(centroids.items())[0][1]) == 2:
                c1, c2 = (0, 1)
            r1 = geo_data.grid.resolution[0]
            r2 = geo_data.grid.resolution[1]

        nkw = {
            "marker": "o",
            "color": "black",
            "markersize": 20,
            "alpha": 0.75
        }
        if node_kwargs is not None:
            nkw.update(node_kwargs)

        tkw = {
            "color": "white",
            "size": 10,
            "ha": "center",
            "va": "center",
            "weight": "ultralight",
            "family": "monospace"
        }
        if label_kwargs is not None:
            tkw.update(label_kwargs)

        lkw = {
            "linewidth": 0.75,
            "color": "black"
        }
        if edge_kwargs is not None:
            lkw.update(edge_kwargs)

        for edge in G.edges():
            a, b = edge
            # plot edges
            plt.plot(np.array([centroids[a][c1], centroids[b][c1]]) * e1 / r1 + d1,
                          np.array([centroids[a][c2], centroids[b][c2]]) * e2 / r2 + d2, **lkw)

            for node in G.nodes():
                plt.plot(centroids[node][c1] * e1 / r1 + d1, centroids[node][c2] * e2 / r2 +d2,
                         marker="o", color="black", markersize=10, alpha=0.75)
                plt.text(centroids[node][c1] * e1 / r1 + d1,
                         centroids[node][c2] * e2 / r2 + d2, str(node), **tkw)

    def plot_gradient(self, scalar_field, gx, gy, gz, cell_number, quiver_stepsize=5, #maybe call r sth. like "stepsize"?
                      direction="y", plot_scalar = True, *args, **kwargs): #include plot data?
        """
            Plot the gradient of the scalar field in a given direction.

            Args:
                geo_data (gempy.DataManagement.InputData): Input data of the model
                scalar_field(numpy.array): scalar field to plot with the gradient
                gx(numpy.array): gradient in x-direction
                gy(numpy.array): gradient in y-direction
                gz(numpy.array): gradient in z-direction
                cell_number(int): position of the array to plot
                quiver_stepsize(int): step size between arrows to indicate gradient
                direction(str): xyz. Caartesian direction to be plotted
                plot_scalar(bool): boolean to plot scalar field
                **kwargs: plt.contour kwargs

            Returns:
                None
        """
        if direction == "y":
            if plot_scalar:
                self.plot_scalar_field(scalar_field, cell_number, direction=direction, plot_data=False)
            U = gx.reshape(self.model.grid.resolution[0], self.model.grid.resolution[1], self.model.grid.resolution[2])[::quiver_stepsize,
                 cell_number, ::quiver_stepsize].T
            V = gz.reshape(self.model.grid.resolution[0], self.model.grid.resolution[1], self.model.grid.resolution[2])[::quiver_stepsize,
                 cell_number, ::quiver_stepsize].T
            plt.quiver(self.model.grid.values[:, 0].reshape(self.model.grid.resolution[0], self.model.grid.resolution[1], self.model.grid.resolution[2])[::quiver_stepsize, cell_number, ::quiver_stepsize].T,
                   self.model.grid.values[:, 2].reshape(self.model.grid.resolution[0], self.model.grid.resolution[1], self.model.grid.resolution[2])[::quiver_stepsize, cell_number, ::quiver_stepsize].T, U, V, pivot="tail",
                   color='blue', alpha=.6)
        elif direction == "x":
            if plot_scalar:
                self.plot_scalar_field(scalar_field, cell_number, direction=direction, plot_data=False)
            U = gy.reshape(self.model.grid.resolution[0], self.model.grid.resolution[1], self.model.grid.resolution[2])[cell_number, ::quiver_stepsize, ::quiver_stepsize].T
            V = gz.reshape(self.model.grid.resolution[0], self.model.grid.resolution[1], self.model.grid.resolution[2])[cell_number, ::quiver_stepsize, ::quiver_stepsize].T
            plt.quiver(self.model.grid.values[:, 1].reshape(self.model.grid.resolution[0], self.model.grid.resolution[1],
                                                            self.model.grid.resolution[2])[cell_number, ::quiver_stepsize,  ::quiver_stepsize].T,
                       self.model.grid.values[:, 2].reshape(self.model.grid.resolution[0], self.model.grid.resolution[1],
                                                            self.model.grid.resolution[2])[cell_number, ::quiver_stepsize,  ::quiver_stepsize].T, U, V,
                       pivot="tail",
                       color='blue', alpha=.6)
        elif direction== "z":
            if plot_scalar:
                self.plot_scalar_field(scalar_field, cell_number, direction=direction, plot_data=False)
            U = gx.reshape(self.model.grid.resolution[0], self.model.grid.resolution[1], self.model.grid.resolution[2])[::quiver_stepsize, ::quiver_stepsize, cell_number].T
            V = gy.reshape(self.model.grid.resolution[0], self.model.grid.resolution[1], self.model.grid.resolution[2])[::quiver_stepsize, ::quiver_stepsize, cell_number].T
            plt.quiver(self.model.grid.values[:, 0].reshape(self.model.grid.resolution[0], self.model.grid.resolution[1],
                                                            self.model.grid.resolution[2])[::quiver_stepsize, ::quiver_stepsize, cell_number].T,
                       self.model.grid.values[:, 1].reshape(self.model.grid.resolution[0], self.model.grid.resolution[1],
                                                            self.model.grid.resolution[2])[::quiver_stepsize, ::quiver_stepsize, cell_number].T, U, V,
                       pivot="tail",
                       color='blue', alpha=.6)
        else:
            raise AttributeError(str(direction) + "must be a cartesian direction, i.e. xyz")

    # TODO: Incorporate to the class
    @staticmethod
    def annotate_plot(frame, label_col, x, y, **kwargs):
        """
        Annotate the plot of a given DataFrame using one of its columns

        Should be called right after a DataFrame or series plot method,
        before telling matplotlib to show the plot.

        Parameters
        ----------
        frame : pandas.DataFrame

        plot_col : str
            The string identifying the column of frame that was plotted

        label_col : str
            The string identifying the column of frame to be used as label

        kwargs:
            Other key-word args that should be passed to plt.annotate

        Returns
        -------
        None

        Notes
        -----
        After calling this function you should call plt.show() to get the
        results. This function only adds the annotations, it doesn't show
        them.
        """
        import matplotlib.pyplot as plt  # Make sure we have pyplot as plt

        for label, x, y in zip(frame[label_col], frame[x], frame[y]):
            plt.annotate(label, xy=(x + 0.2, y + 0.15), **kwargs)

