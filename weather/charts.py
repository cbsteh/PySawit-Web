import base64
import math
from collections import Counter, OrderedDict
from io import BytesIO

import matplotlib
import matplotlib.ticker
import numpy
from scipy.stats import exponweib
from scipy.stats import gamma
from scipy.stats import kurtosis
from scipy.stats import rv_continuous
from scipy.stats import skew

matplotlib.use('Agg')
import matplotlib.pyplot as plt


def roundup(x):
    return int(math.ceil(x / 10.0)) * 10


def mround(val, n=2):
    return round(val, n) + 0    # prevents 'negative zero' (e.g., -0.009 -> -0.0)


class InvalidWeatherFile(ValueError):
    def __init__(self, msg):
        msg += ' This file should not be used in simulations. Please delete this file and reupload.'
        super(InvalidWeatherFile, self).__init__(msg)


class WeatherStats:
    axis_sens = 0.75

    def __init__(self, filename):
        self.data = None
        self.figures = []
        self.stats = dict()
        self.csv_load(filename)

    def csv_load(self, filename):
        keys = None
        headers_found = False
        doypos = -1

        lines = []
        for line in open(filename, 'r'):
            tline = line.strip()
            if tline:
                lines.append(tline)

        prev_doy = 0
        for cur_line in [line for line in lines if line[0] != '#']:
            tokens = [token for token in cur_line.split(',') if token.strip()]
            if not headers_found:
                keys = [key.strip('*') for key in tokens]

                if Counter(keys).most_common()[0][1] > 1:
                    raise InvalidWeatherFile('Duplicate headers found.')
                else:
                    man_keys = {'doy', 'tmin', 'tmax', 'rain'}
                    if not man_keys.intersection(set(keys)) == man_keys:
                        raise InvalidWeatherFile('One or more required headers are missing.')

                doypos = keys.index('doy')
                fields = [field for field in keys if field != 'doy']
                self.data = dict([(i + 1, dict([(f, []) for f in fields])) for i in range(365)])
                headers_found = True
            else:
                try:
                    doy = int(tokens[doypos])
                except ValueError:
                    raise InvalidWeatherFile('Day of year is not numeric.')

                if doy < 1 or doy > 365:
                    raise InvalidWeatherFile('Day of year is out of range.')
                if (doy - prev_doy) > 1:
                    raise InvalidWeatherFile('Weather data is not continuous. Missing values?')

                prev_doy = doy if doy < 365 else 0
                if len(keys) != len(tokens):
                    raise InvalidWeatherFile('Weather data mismatch or missing.')
                z = zip(keys, tokens)

                try:
                    gen = [(field, float(val)) for field, val in z if field != 'doy']
                except ValueError:
                    raise InvalidWeatherFile('Non-numeric weather data found.')

                for field, val in gen:
                    self.data[doy][field].append(val)

        if not self.data[1]['tmin']:
            raise InvalidWeatherFile('File has no weather data!')

    def sum_y(self, field):
        maxyrs = len(self.data[1][field])
        ydict = dict([(i, 0.0) for i in range(maxyrs)])
        yrs = []
        for doy in range(365):
            vals = self.data[doy+1][field]
            yrs.append(len(vals))
            for yr, y in enumerate(vals):
                ydict[yr] += y

        minyrs = min(yrs)
        for i in range(maxyrs-minyrs):
            ydict.pop(maxyrs-i-1)

        return ydict

    def avg_y(self, field):
        maxyrs = len(self.data[1][field])
        ydict = dict([(i, 0.0) for i in range(maxyrs)])
        yrs = []
        for doy in range(365):
            vals = self.data[doy+1][field]
            yrs.append(len(vals))
            for yr, y in enumerate(vals):
                ydict[yr] += y / 365

        minyrs = min(yrs)
        for i in range(maxyrs-minyrs):
            ydict.pop(maxyrs-i-1)

        return ydict

    def get_xy(self, field):
        xlst = []
        ylst = []
        for doy in range(365):
            vals = self.data[doy+1][field]
            for y in vals:
                xlst.append(doy+1)
                ylst.append(y)
        return xlst, ylst

    def get_y(self, field):
        ylst = []
        maxlen = len(self.data[1][field])
        for n in range(maxlen):
            for doy in range(365):
                par = self.data[doy+1][field]
                if n < len(par):
                    ylst.append(par[n])
        return ylst

    def set_ylmt(self, ax, yvals, change_ymin=True):
        min_yval = min(yvals)
        max_yval = max(yvals)
        min_yaxis, max_yaxis = ax.get_ylim()
        locs = plt.yticks()[0]
        scale = abs(abs(locs[1]) - abs(locs[0]))
        if abs(abs(max_yaxis) - abs(max_yval)) < self.axis_sens * scale:
            max_yaxis += scale
            ax.set_ylim(top=max_yaxis)
        if change_ymin:
            if abs(abs(min_yval) - abs(locs[0])) < self.axis_sens * scale:
                min_yaxis = locs[0] - scale
                if min_yaxis >= 0.0:
                    ax.set_ylim(bottom=min_yaxis)
                else:
                    ax.set_ylim(bottom=0.0)

    def plot_scatter_sum(self, field, field_label='', fig_caption='', start_0=False):
        ydict = self.sum_y(field)
        if not ydict:
            return

        numyears = len(ydict)
        xlst = [i+1 for i in range(numyears)]
        ylst = [ydict[i] for i in range(numyears)]

        with BytesIO() as image:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_xlabel('year no.')
            ax.set_ylabel(field_label if field_label else field)
            ax.plot(xlst, ylst, 'ro', markersize=2)

            if start_0:
                ax.set_ylim(ymin=0)
            self.set_ylmt(ax, ylst, not start_0)

            fig.savefig(image, format='png', transparent=True)
            image_base64 = base64.b64encode(image.getvalue()).decode('utf-8').replace('\n', '')
            self.figures.append([fig_caption, image_base64])
            plt.close(fig)

    def plot_scatter_avg(self, field, field_label='', fig_caption='', start_0=False):
        ydict = self.avg_y(field)
        if not ydict:
            return

        numyears = len(ydict)
        xlst = [i+1 for i in range(numyears)]
        ylst = [ydict[i] for i in range(numyears)]

        with BytesIO() as image:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_xlabel('year no.')
            ax.set_ylabel(field_label if field_label else field)
            ax.plot(xlst, ylst, 'ro', markersize=2)

            if start_0:
                ax.set_ylim(ymin=0)
            self.set_ylmt(ax, ylst, not start_0)

            fig.savefig(image, format='png', transparent=True)
            image_base64 = base64.b64encode(image.getvalue()).decode('utf-8').replace('\n', '')
            self.figures.append([fig_caption, image_base64])
            plt.close(fig)

    def plot_scatter(self, field, field_label='', fig_caption='', start_0=False):
        xlst, ylst = self.get_xy(field)
        if not (xlst and ylst):
            return

        with BytesIO() as image:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_xlabel('doy')
            ax.set_xlim(1, 365)

            ticks = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365]
            major_ticks = []
            for i, tick in enumerate(ticks):
                if i % 2 == 0:
                    major_ticks.append(tick)
                else:
                    major_ticks.append('')

            ax.set_xticks(ticks)
            ax.set_xticklabels(major_ticks)
            ax.set_ylabel(field_label if field_label else field)
            ax.plot(xlst, ylst, 'bo', markersize=2 if len(ylst) < 730 else 1, alpha=0.3)

            if start_0:
                ax.set_ylim(ymin=0)
            self.set_ylmt(ax, ylst, not start_0)

            fig.savefig(image, format='png', transparent=True)
            image_base64 = base64.b64encode(image.getvalue()).decode('utf-8').replace('\n', '')
            self.figures.append([fig_caption, image_base64])
            plt.close(fig)

    def plot_1d(self, field, field_label='', fig_caption=''):
        ylst = self.get_y(field)
        if not ylst:
            return

        with BytesIO() as image:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_ylabel(field_label if field_label else field)
            ax.plot(ylst, 'bo', markersize=2 if len(ylst) < 730 else 1)
            fig.savefig(image, format='png', transparent=True)
            image_base64 = base64.b64encode(image.getvalue()).decode('utf-8').replace('\n', '')
            self.figures.append([fig_caption, image_base64])
            plt.close(fig)

    def plot_histogram(self, field, field_label='', fig_caption=''):
        xlst, ylst = self.get_xy(field)
        if not (xlst and ylst):
            return

        with BytesIO() as image:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_xlabel(field_label if field_label else field)
            ax.set_ylabel('no. of days')
            y, x, _ = ax.hist(ylst, density=True, histtype='step')

            maxy = max(y)
            scale = (maxy - min(y)) / (len(y) - 1)
            max_yticks = max(ax.get_yticks())
            if max_yticks - maxy < self.axis_sens * scale:
                max_yticks += scale
                ax.set_ylim(top=max_yticks)

            h = x[1] - x[0]
            total_days = len(ylst)
            ylabels = []
            for density in ax.get_yticks():
                num_days = int(density * h * total_days)
                ylabels.append(str(num_days))
            ax.set_yticklabels(ylabels)

            if field == 'rain':
                h = (max(ylst) - min(ylst)) / 8
                if h > 10:
                    tick_spacing = roundup(h)
                    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(tick_spacing))

            fig.savefig(image, format='png', transparent=True)
            image_base64 = base64.b64encode(image.getvalue()).decode('utf-8').replace('\n', '')
            self.figures.append([fig_caption, image_base64])
            plt.close(fig)

    @staticmethod
    def set_plot():
        params = {
            'font.size': 10,
            'figure.subplot.left': 0.25,
            'figure.subplot.bottom': 0.2,
            'figure.figsize': (4, 4),
            'axes.spines.right': False,
            'axes.spines.top': False,
        }
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)
        matplotlib.rcParams.update(params)

    def stats_descriptive(self, field=None, lst=None):
        if not lst:
            lst = self.get_y(field)
        arr = numpy.array(lst)
        avg = mround(float(numpy.mean(arr)), 2)
        median = mround(float(numpy.median(arr)), 2)
        sd = mround(float(numpy.std(arr)), 2)
        minval = numpy.min(arr)
        maxval = numpy.max(arr)
        ret = [
            ('Count, N', arr.size),
            ('Range (min, max)', '({}, {})'.format(minval, maxval)),
            ('Mean \xb1 1 standard deviation', '{} \xb1 {}'.format(avg, sd)),
            ('Median', median),
        ]
        return ret

    def stats_min_air_temp(self):
        lst = self.get_y('tmin')
        d = OrderedDict(self.stats_descriptive(lst=lst))
        arr = numpy.array(lst)
        d.update([
            ('Skewness', mround(float(skew(arr)), 2)),
            ('Kurtosis', mround(float(kurtosis(arr)), 2)),
        ])
        self.stats.update({'tmin': d})

    def stats_max_air_temp(self):
        lst = self.get_y('tmax')
        d = OrderedDict(self.stats_descriptive(lst=lst))
        arr = numpy.array(lst)
        d.update([
            ('Skewness', mround(float(skew(arr)), 2)),
            ('Kurtosis', mround(float(kurtosis(arr)), 2)),
        ])
        self.stats.update({'tmax': d})

    def stats_wind(self):
        lst = self.get_y('wind')
        d = OrderedDict(self.stats_descriptive(lst=lst))
        shape, scale = rv_continuous.fit(exponweib, lst, fa=1, floc=0)[1::2]
        d.update([
            ('Weibull shape', mround(shape, 2)),
            ('Weibull scale', mround(scale, 2)),
        ])
        self.stats.update({'wind': d})

    def stats_rain(self):
        min_rain = 0.2
        nwd, nww, nd, nw = 0, 0, 0, 0  # no. of wet-dry, wet-wet, dry, and wet days
        lst = self.get_y('rain')
        total_days = len(lst)
        nday = 0
        # count number of dry and wet days; checks two consecutive days per loop cycle
        while nday + 1 < total_days:
            # a rain day if rainfall > 0.0
            rain1 = lst[nday] > min_rain  # any rain on day (t)?
            rain2 = lst[nday + 1] > min_rain  # any rain on the next day (t+1)?
            if not rain1 and rain2:  # a dry day, followed by a wet day
                nwd += 1
            if rain1 and rain2:  # a wet day, followed by another wet day
                nww += 1
            if not rain1:  # count the number of dry days
                nd += 1
            # need to check the rain status on the last day
            #   because this loop checks every two consecutive days (not every day)
            if (nday + 1) == (total_days - 1) and not rain2:
                nd += 1  # the last day is a dry day
            nday += 1
        # finished counting the number of dry and wet days, so now calculate the probabilities:
        nw = total_days - nd
        try:
            pwd = mround(nwd / nd, 2)  # P(W|D) - dry then wet day
            pww = mround(nww / nw, 2)  # P(W|W) - both wet days
            pdd = mround(1 - pwd, 2)  # P(D|D) - both dry days
            pdw = mround(1 - pww, 2)  # P(D|W) - wet then dry day
            pw = mround(nw / total_days, 2)  # P(W) - a wet day
            pd = mround(nd / total_days, 2)  # P(D) - a dry day
        except ZeroDivisionError:
            pwd = pww = pdd = pdw = pw = pd = '(Insufficient data)'

        d = OrderedDict(self.stats_descriptive(lst=lst))
        d.update([
            ('No. of wet (W) days', nw),
            ('No. of dry (D) days', nd),
            ('Probability of a wet day, P(W)', pw),
            ('Probability of a dry day, P(D)', pd),
            ('Probability of a wet, then dry day, P(W|D)', pwd),
            ('Probability of a dry, then wet day, P(D|W)', pdw),
            ('Probability of two consecutive wet days, P(W|W)', pww),
            ('Probability of two consecutive dry days, P(D|D)', pdd),
        ])

        lst = [v for v in lst if v > 0.0]   # fit only to non-zero values (rainfall days)
        # can only fit a gamma function with 2 or more values:
        if len(lst) > 1:
            shape, scale = rv_continuous.fit(gamma, lst, floc=0)[::2]  # location set to zero
            d.update([
                ('Gamma shape', mround(shape, 2)),
                ('Gamma scale', mround(scale, 2)),
            ])
        else:
            d.update([
                ('Gamma shape', '(Insufficient data)'),
                ('Gamma scale', '(Insufficient data)'),
            ])

        self.stats.update({'rain': d})
