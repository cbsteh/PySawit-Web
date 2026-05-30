import base64
import math
from io import BytesIO

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt


class Charts(object):
    colors = ['black', 'red', 'blue', 'green', 'magenta', 'cyan']

    def __init__(self, initial_age, daydict, anndict):
        self.initial_age = initial_age
        self.anndict = anndict
        self.figures = []
        self.yearticks = []
        self.dayticks = []
        self.is_annual_plot = True

        dct = {}
        for key, vals in daydict.items():
            dct.update({key: [float(val) for val in vals]})
        self.daydict = dct

    def set_yearticks(self):
        maxyear = len(self.anndict['year'])
        if maxyear > 1:
            start_at = 0 if (10 < maxyear <= 20) and (maxyear % 2 == 0) else 1
            h = 1 if maxyear < 11 else 2
            self.yearticks = [i for i in range(start_at, maxyear+1, h)]
        else:
            self.yearticks = []

    def set_dayticks(self):
        xlen = len(self.daydict['age'])
        xticks = []
        if xlen > 1:
            initial = self.initial_age
            last = xlen + initial - 1
            n = xlen / 365
            if n <= 6:
                xticks = [i + initial for i in range(0, xlen, 365)]
                if xticks[-1] < last:
                    xticks.append(xticks[-1] + 365)
            else:
                hsize = math.ceil(xlen / 6)
                if hsize % 365 > 0:
                    n = int(hsize / 365)
                    hsize = 365 * (n + 1)
                xticks = [i + initial for i in range(0, xlen + 1, hsize)]
                if xticks[-1] < last:
                    xticks.append(xticks[-1] + hsize)
        self.dayticks = xticks

    def plot(self, ylst, ylabels, axis_xlabel, axis_ylabel, fig_caption, force_to_0=True):
        with BytesIO() as image:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_xlabel(axis_xlabel)
            ax.set_ylabel(axis_ylabel)

            initial = 1 if self.is_annual_plot else self.initial_age
            x = [i+initial for i in range(len(ylst[0]))]
            for i, y in enumerate(ylst):
                ax.plot(x, y, color=Charts.colors[i], label=ylabels[i])

            if self.is_annual_plot:
                ax.set_xticks(self.yearticks)
                ax.set_xlim(xmin=self.yearticks[0], xmax=self.yearticks[-1])
            else:
                ax.set_xticks(self.dayticks)
                ax.set_xlim(xmin=self.dayticks[0], xmax=self.dayticks[-1])

            if force_to_0:
                ax.set_ylim(ymin=0)

            ax.yaxis.set_major_locator(plt.MaxNLocator(8))
            yticks = ax.get_yticks()
            ax.set_ylim(ymin=yticks[0], ymax=yticks[-1])

            col = len(ylst)
            ax.legend(bbox_to_anchor=(0.0, 1.02, 1.0, 0.102),
                      loc=3,
                      ncol = col if col < 4  else 3,
                      mode='expand',
                      borderaxespad=0.,
                      framealpha=0)

            fig.savefig(image, format='png', transparent=True)
            image_base64 = base64.b64encode(image.getvalue()).decode('utf-8').replace('\n', '')
            self.figures.append([fig_caption, image_base64])
            plt.close(fig)

    def plot_radiation(self, dct):
        tot = dct['totalrad']
        dr = dct['directrad']
        df = dct['diffuserad']
        self.plot([tot, dr, df],
                  ['total', 'direct', 'diffuse'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'solar radiation (MJ m$^{-2}$ ' +
                  (r'yr$^{-1}$)' if self.is_annual_plot else r'day$^{-1}$)'),
                  'Solar radiation components')

    def plot_rain(self, dct):
        gross = dct['rain']
        net = dct['netrain']
        self.plot([gross, net],
                  ['gross', 'net'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'rainfall (mm ' + (r'yr$^{-1}$)' if self.is_annual_plot else r'day$^{-1}$)'),
                  'Rainfall components: gross (above canopies) and net (below canopies)')

    def plot_yield(self, dct):
        opyield = dct['yield']
        self.plot([opyield],
                  ['yield'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'FFB yield (kg palm$^{-1}$ ' +
                  (r'yr$^{-1}$)' if self.is_annual_plot else r'day$^{-1}$)'),
                  'Fresh fruit bunches (FFB) yield (dry weight)')

    def plot_flowersex(self, dct):
        flo = dct['flowersex']
        self.plot([flo],
                  ['%female'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'% female flowers',
                  'Proportion of female flowers')

    def plot_lai(self, dct):
        lai = dct['LAI']
        self.plot([lai],
                  ['LAI'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'LAI (m$^2$ m$^{-2}$)',
                  'Leaf area index (LAI)')

    def plot_vdmwgts(self, dct):
        pinnae = dct['pinnae']
        rachis = dct['rachis']
        fronds = dct['fronds']
        roots = dct['roots']
        trunk = dct['trunk']
        self.plot([pinnae, rachis, fronds, roots, trunk],
                  ['pinnae', 'rachis', 'fronds', 'roots', 'trunk'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'kg palm$^{-1}$',
                  'Dry weight of tree parts')

    def plot_flowerwgts(self, dct):
        male = dct['male']
        female = dct['female']
        bunches = dct['bunches']
        self.plot([male, female, bunches],
                  ['male', 'female', 'bunches'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'kg palm$^{-1}$',
                  'Dry weight of flowers and bunches')

    def plot_vdm_tdm_growth(self, dct):
        vdm = dct['VDM_growth']
        tdm = dct['TDM_growth']
        self.plot([vdm, tdm],
                  ['VDM', 'TDM'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'kg palm$^{-1}$ ' + (r'yr$^{-1}$' if self.is_annual_plot else r'day$^{-1}$'),
                  'Increment in vegetative (VDM) and total (TDM) dry matter')

    def plot_trunkhgt(self, dct):
        hgt = dct['trunk_hgt']
        self.plot([hgt],
                  ['trunk height'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'height (m)',
                  'Trunk height')

    def plot_assim(self, dct):
        photosyn = dct['assim_photosyn']
        maint = dct['assim_maint']
        growth = dct['assim_growth']
        gengro = dct['assim_gen']
        self.plot([photosyn, maint, growth, gengro],
                  ['P', 'M', 'Ggro', 'Ggen'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'kg CH$_2$O palm$^{-1}$ ' +
                  (r'yr$^{-1}$' if self.is_annual_plot else r'day$^{-1}$'),
                  ('Gross photosyntesis (P) and the respiration components: '
                   'maintenace (M), growth (Ggro), and generative organ (Ggen)'))

    def plot_BI(self, dct):
        bi = dct['BI']
        self.plot([bi],
                  ['BI'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'BI',
                  'Bunch index (BI)')

    def plot_CGR(self, dct):
        cgr = dct['CGR']
        self.plot([cgr],
                  ['CGR'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'CGR (t ha$^{-1}$ yr$^{-1}$)',
                  'Crop growth rate (CGR)')

    def plot_NAR(self, dct):
        nar = dct['NAR']
        self.plot([nar],
                  ['NAR'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'NAR (g m$^{-2}$ week$^{-1}$)',
                  'Net assimilation rate (NAR)')

    def plot_rootdepth(self, dct):
        rootdepth = dct['rootdepth']
        self.plot([rootdepth],
                  ['rooting depth'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'depth (m)',
                  'Rooting depth')

    def plot_wind(self, dct):
        wind = dct['wind']
        self.plot([wind],
                  ['wind speed'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'wind speed (m s$^{-1}$)',
                  'Mean wind speed')

    def plot_tmean(self, dct):
        tmean = dct['tmean']
        self.plot([tmean],
                  ['air temperature'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'air temperature ($^\circ$C)',
                  'Mean air temperature',
                  False)

    def plot_tminmax(self, dct):
        tmin = dct['tmin']
        tmax = dct['tmax']
        self.plot([tmin, tmax],
                  ['Tmin', 'Tmax'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'air temperature ($^\circ$C)',
                  'Minimum (Tmin) and maximum (Tmax) air temperature',
                  False)

    def plot_ambientCO2(self, dct):
        co2 = dct['ambientCO2']
        self.plot([co2],
                  [r'ambient CO$_2$'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'ambient CO$_2$ ($\mu$mol mol$^{-1}$)',
                  'Ambient carbon dioxide (CO2) concentration',
                  False)

    def plot_rootzoneVWC(self, dct):
        root = dct['rootzone_VWC']
        self.plot([root],
                  ['root zone VWC'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'VWC (m$^{3}$ m$^{-3}$)',
                  'Volumetric soil water content (VWC) within the root zone')

    def plot_actualET(self, dct):
        et = dct['actual_ET']
        e = dct['actual_E']
        t = dct['actual_T']
        self.plot([et, e, t],
                  ['ET', 'E', 'T'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'water loss (mm ' + (r'yr$^{-1}$)' if self.is_annual_plot else r'day$^{-1}$)'),
                  ('Actual water loss by soil evaporation (E), '
                  'plant transpiration (T), and their total (ET)'))

    def plot_waterdeficit(self, dct):
        deficit = dct['waterdeficit']
        self.plot([deficit],
                  ['water deficit'],
                  'year' if self.is_annual_plot else 'palm age (days)',
                  r'water deficit (mm ' +
                  (r'yr$^{-1}$)' if self.is_annual_plot else r'day$^{-1}$)'),
                  'Plant water deficit')

    def plot_soillayer(self, dct, fieldtemplate, legend, caption, force_to_0=True):
        fields = [fieldtemplate.format(i+1) for i in range(6)]
        layers = [dct.get(field) for field in fields]

        data = []
        datalabels = []
        n = 0
        while n < 6 and layers[n]:
            data.append(layers[n])
            datalabels.append('layer{0}'.format(n+1))
            n += 1

        self.plot(data,
                  datalabels,
                  'year' if self.is_annual_plot else 'palm age (days)',
                  legend,
                  caption,
                  force_to_0=force_to_0)

    def plot_soilT(self, dct):
        self.plot_soillayer(dct,
                            'layer{0}_t',
                            r'plant water uptake (mm ' +
                            (r'yr$^{-1}$)' if self.is_annual_plot else r'day$^{-1}$)'),
                            'Plant water uptake from ech soil layer')

    def plot_soilVWC(self, dct):
        self.plot_soillayer(dct,
                            'layer{0}_VWC',
                            r'water content (m$^3$ m$^{-3}$)',
                            'Volumetric water content in each soil layer')

    def plot_soilinflux(self, dct):
        self.plot_soillayer(dct,
                            'layer{0}_influx',
                            r'water influx (mm ' +
                            (r'yr$^{-1}$)' if self.is_annual_plot else r'day$^{-1}$)'),
                            'Influx of water into each soil layer')

    def plot_soiloutflux(self, dct):
        self.plot_soillayer(dct,
                            'layer{0}_outflux',
                            r'water outflux (mm ' +
                            (r'yr$^{-1}$)' if self.is_annual_plot else r'day$^{-1}$)'),
                            'Outflux of water from each soil layer')

    def plot_soilnetflux(self, dct):
        self.plot_soillayer(dct,
                            'layer{0}_netflux',
                            r'water net flux (mm ' +
                            (r'yr$^{-1}$)' if self.is_annual_plot else r'day$^{-1}$)'),
                            'Net flux of water for each soil layer',
                            False)


    def plot_all(self, annual):
        groups = []
        self.is_annual_plot = annual
        if annual:
            dct = self.anndict
        else:
            dct = self.daydict

        if len(dct['yield']) > 1:
            params = {
                'font.size': 10,
                'figure.subplot.left': 0.25,
                'figure.subplot.bottom': 0.2,
                'figure.subplot.top': 0.85,
                'figure.figsize': (4, 4),
                'axes.spines.right': False,
                'axes.spines.top': False,
                'legend.handlelength': 1.2,
            }
            matplotlib.rcParams.update(matplotlib.rcParamsDefault)
            matplotlib.rcParams.update(params)

            if self.is_annual_plot:
                self.set_yearticks()
            else:
                self.set_dayticks()

            # yield components:
            self.plot_yield(dct)
            self.plot_flowerwgts(dct)
            if self.is_annual_plot:
                self.plot_BI(dct)
                self.plot_CGR(dct)
                self.plot_NAR(dct)
            groups.append(self.figures)
            self.figures = []

            # crop:
            self.plot_assim(dct)
            self.plot_lai(dct)
            self.plot_vdmwgts(dct)
            self.plot_vdm_tdm_growth(dct)
            self.plot_trunkhgt(dct)
            self.plot_rootdepth(dct)
            groups.append(self.figures)
            self.figures = []

            # stresses:
            self.plot_waterdeficit(dct)
            self.plot_actualET(dct)
            if self.is_annual_plot:
                self.plot_flowersex(dct)
            groups.append(self.figures)
            self.figures = []

            # water:
            self.plot_soilVWC(dct)
            self.plot_rootzoneVWC(dct)
            self.plot_soilT(dct)
            self.plot_soilnetflux(dct)
            self.plot_soilinflux(dct)
            self.plot_soiloutflux(dct)
            groups.append(self.figures)
            self.figures = []

            # environment:
            self.plot_rain(dct)
            self.plot_radiation(dct)
            self.plot_wind(dct)
            if self.is_annual_plot:
                self.plot_tmean(dct)
            else:
                self.plot_tminmax(dct)
            self.plot_ambientCO2(dct)
            groups.append(self.figures)
            self.figures = groups

        return self.figures

    def plot_batch(self,
                   x,
                   ylst, ylabels,
                   axis_xlabel, axis_ylabel,
                   fig_caption, force_to_0=True,
                   scatter=True):
        params = {
            'figure.subplot.left': 0.15,
            'axes.spines.right': False,
            'axes.spines.top': False,
        }
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)
        matplotlib.rcParams.update(params)

        with BytesIO() as image:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_xlabel(axis_xlabel)

            i = 0
            pos = 0
            while pos != -1 and i < 3:
                pos = axis_ylabel.find(',', pos+1)
                if i == 2 and pos != -1:
                    axis_ylabel = axis_ylabel[:pos] + '\n' + axis_ylabel[pos+2:]
                i += 1

            ax.set_ylabel(axis_ylabel)

            for i, y in enumerate(ylst):
                if scatter:
                    ax.plot(x, y, '.', color=Charts.colors[i % len(self.colors)], label=ylabels[i])
                else:
                    ax.plot(x, y, color=Charts.colors[i % len(self.colors)], label=ylabels[i])

            ax.xaxis.set_major_locator(plt.MaxNLocator(10))
            xticks = ax.get_xticks()
            ax.set_xlim(xmin=xticks[0], xmax=xticks[-1])

            if force_to_0:
                ax.set_ylim(ymin=0)

            ax.yaxis.set_major_locator(plt.MaxNLocator(8))
            yticks = ax.get_yticks()
            ax.set_ylim(ymin=yticks[0], ymax=yticks[-1])

            col = len(ylst)
            ax.legend(bbox_to_anchor=(0.0, 1.02, 1.0, 0.102),
                      loc=3,
                      ncol = col if col < 4  else 3,
                      mode='expand',
                      borderaxespad=0.,
                      framealpha=0)

            fig.savefig(image, format='png', transparent=True)
            image_base64 = base64.b64encode(image.getvalue()).decode('utf-8').replace('\n', '')
            plt.close(fig)
            return [fig_caption, image_base64]
