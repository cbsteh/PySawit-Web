from collections import OrderedDict
from functools import reduce


class OutputSummary(object):
    total365 = ['totalrad', 'directrad', 'diffuserad', 'rain', 'netrain', 'flowersex',
                'assim_photosyn', 'assim_maint', 'assim_growth', 'assim_gen',
                'VDM_growth', 'TDM_growth', 'yield', 'actual_E', 'actual_T', 'pot_T',
                'actual_ET', 'waterdeficit', 'layer{0}_t',
                'layer{0}_influx', 'layer{0}_outflux', 'layer{0}_netflux', 'layer{0}_t']

    at365 = ['ambientCO2', 'LAI', 'pinnae', 'rachis', 'fronds', 'roots', 'trunk',
             'male', 'female', 'bunches', 'trunk_hgt', 'rootdepth',
             'rootzone_VWC', 'layer{0}_VWC']

    avg365 = ['wind']

    def __init__(self, filename, plantdens, nlayers):
        self.filename = filename
        self.plantdens = plantdens
        self.nlayers = nlayers
        self.daily = None       # Ordered dictionary holding all daily values
        self.annual = None      # Ordered dictionary holding all annual values

    def load_all_values(self):
        odct = OrderedDict()
        with open(self.filename, 'r') as fin:
            bfound_headers = False
            headers = []
            # parse each line in the file:
            for txtline in fin:
                # skip all comment lines:
                if txtline.lstrip(' ')[0] == '#':
                    continue

                # create a list of text read from each line in the file:
                txtlst = [txt.strip(' ').strip('\n') for txt in txtline.split(',')]

                if not bfound_headers:
                    # line after comment are headers, and each header is a dictionary key
                    headers = txtlst[:]
                    odct.update([(key, []) for key in txtlst])
                    bfound_headers = True  # finished with headers, next read in only data
                else:
                    for k, v in zip(headers, txtlst):
                        odct[k].append(v)

        # now convert all read values into floats:
        self.daily = OrderedDict()
        for key, vals in odct.items():
            if key in ['age',]:
                self.daily.update({key: [int(val) for val in vals]})
            else:
                self.daily.update({key: [float(val) for val in vals]})

        # create one for fronds:
        self.daily.update({'fronds': []})
        for n in range(len(self.daily['pinnae'])):
            self.daily['fronds'].append(self.daily['pinnae'][n] + self.daily['rachis'][n])

        # create one for plant water deficit:
        self.daily.update({'waterdeficit': []})
        for n in range(len(self.daily['pot_T'])):
            self.daily['waterdeficit'].append(self.daily['pot_T'][n] - self.daily['actual_T'][n])

        # create one for actual total ET:
        self.daily.update({'actual_ET': []})
        for n in range(len(self.daily['actual_T'])):
            self.daily['actual_ET'].append(self.daily['actual_E'][n] + self.daily['actual_T'][n])

    @staticmethod
    def get_slices(array, slice_length, skip_length=0, skip_first=False, equal_length=True):
        ret = []
        array_length = len(array)
        for i in range(array_length):
            first = i * (slice_length + skip_length)
            if skip_first:
                first += skip_length
            last = first + slice_length
            if (first >= array_length):
                break
            ar = array[first:last]
            if equal_length and len(ar) != slice_length:
                break
            ret.append(ar)
        return ret

    @staticmethod
    def annual_total(array):
        slices = OutputSummary.get_slices(array, slice_length=365)
        totals = []
        for arr in slices:
            totals.append(reduce(lambda x, y: x + y, arr))
        return totals

    @staticmethod
    def annual_value(array):
        slices = OutputSummary.get_slices(array, slice_length=1, skip_length=364, skip_first=True)
        lastvals = []
        for arr in slices:
            lastvals.extend(arr)
        return lastvals

    @staticmethod
    def annual_mean(array):
        slices = OutputSummary.get_slices(array, slice_length=365)
        totals = []
        for arr in slices:
            totals.append(reduce(lambda x, y: x + y, arr))
        totals = [val / 365 for val in totals]
        return totals

    @staticmethod
    def annual_mean_pair(array1, array2):
        array = [(v1 + v2) / 2 for v1, v2 in zip(array1, array2)]
        slices = OutputSummary.get_slices(array, slice_length=365)
        totals = []
        for arr in slices:
            totals.append(reduce(lambda x, y: x + y, arr))
        totals = [val / 365 for val in totals]
        return totals

    def set_annual(self):
        def set_a(keys, fn):
            for key in keys:
                if 'layer{0}' in key:
                    for nlayer in range(self.nlayers):
                        k = key.format(nlayer + 1)
                        self.annual[k] = fn(self.daily[k])
                else:
                    self.annual[key] = fn(self.daily[key])

        def set_b(key, fn):
            if 'layer{0}' in key:
                for nlayer in range(self.nlayers):
                    k = key.format(nlayer + 1)
                    self.annual[k] = fn(self.daily[k])
            else:
                self.annual[key] = fn(self.daily[key])

        self.annual = OrderedDict()
        ann = self.annual
        ann['year'] = []
        ann['tmean'] = None
        ann['totalrad'] = None
        ann['directrad'] = None
        ann['diffuserad'] = None
        ann['wind'] = None
        ann['rain'] = None
        ann['netrain'] = None
        ann['ambientCO2'] = None
        ann['LAI'] = None
        ann['pinnae'] = None
        ann['rachis'] = None
        ann['fronds'] = None
        ann['trunk'] = None
        ann['roots'] = None
        ann['male'] = None
        ann['female'] = None
        ann['bunches'] = None
        ann['flowersex'] = None
        ann['assim_photosyn'] = None
        ann['assim_maint'] = None
        ann['assim_growth'] = None
        ann['assim_gen'] = None
        ann['VDM_growth'] = None
        ann['TDM_growth'] = None
        ann['yield'] = None
        ann['trunk_hgt'] = None
        ann['rootdepth'] = None
        ann['rootzone_VWC'] = None
        ann['actual_E'] = None
        ann['actual_T'] = None
        ann['pot_T'] = None
        ann['actual_ET'] = None
        ann['waterdeficit'] = None

        set_a(OutputSummary.total365, OutputSummary.annual_total)
        set_a(OutputSummary.at365, OutputSummary.annual_value)
        set_a(OutputSummary.avg365, OutputSummary.annual_mean)
        ann['tmean'] = OutputSummary.annual_mean_pair(self.daily['tmin'], self.daily['tmax'])
        ann['BI'] = []
        ann['CGR'] = []
        ann['NAR'] = []
        nyrs = self.numyears()
        for i in range(nyrs):
            ann['year'].append(i + 1)
            ann['flowersex'][i] = (ann['flowersex'][i] / 365) * 100
            tot = ann['VDM_growth'][i] + ann['yield'][i]
            ann['BI'].append(ann['yield'][i] / tot)
            ann['CGR'].append(tot * self.plantdens / 1000)
            ann['NAR'].append(ann['CGR'][i] / ann['LAI'][i] * 100 / 52)

    def numyears(self):
        return len(self.annual[OutputSummary.at365[0]])

    def summarize(self):
        self.load_all_values()
        self.set_annual()

    def annual_as_file(self, filename):
        nkeys = len(self.annual.keys())
        fmt0 = ('{:>15},' * nkeys)[:-1] + '\n'
        fmt1 = '{:>15d},' + ('{:>15.3f},' * (nkeys - 1))[:-1] + '\n'
        with open(filename, 'wt') as fout:
            headers = [key for key in self.annual.keys()]
            fout.write(fmt0.format(*headers))
            for yr in range(self.numyears()):
                datalst = [self.annual[key][yr] for key in self.annual.keys()]
                fout.write(fmt1.format(*datalst))

    def annual_as_table(self):
        headers = [key for key in self.annual.keys()]
        thead = ''
        for header in headers:
            id = header.replace('_', '-')
            thead += '<th class="param-%s">%s</th>' % (id, header)

        for ch in ['1', '2', '3', '4', '5', '6']:
            thead = thead.replace('param-layer'+ch, 'param-layer')

        thead = thead.replace('_', '_<br/>')
        po = '<td data-toggle="popover" data-content="{}">'

        fmt = '<tr>' + po + '{:d}</td>' + (po + '{:.3f}</td>') * (len(headers) - 1) + '</tr>'
        tbody = ''
        for yr in range(self.numyears()):
            nyr = yr + 1
            datalst = [(nyr, self.annual[key][yr]) for key in self.annual.keys()]
            datalst = [item for sublist in datalst for item in sublist]
            tbody += fmt.format(*datalst)

        fmt = '<thead><tr>{0}</tr></thead><tbody>{1}</tbody>'
        html = fmt.format(thead, tbody)
        return html

    def daily_as_table(self):
        daily = self.daily
        fn = OutputSummary.get_slices
        daily365 = OrderedDict([(k, fn(daily[k], 365, equal_length=False)) for k in daily.keys()])

        headers = [key for key in self.daily.keys()]
        thead = ''
        for header in headers:
            id = header.replace('_', '-')
            thead += '<th class="param-%s">%s</th>' % (id, header)

        for ch in ['1', '2', '3', '4', '5', '6']:
            thead = thead.replace('param-layer'+ch, 'param-layer')

        thead = thead.replace('_', '_<br/>')
        fmt0 = '<tr>'
        for key in headers:
            po = '<td data-toggle="popover" data-content="{} days ({:.3f} yrs)">'
            if key in ['age',]:
                fmt0 += po +'{:d}</td>'
            else:
                fmt0 += po + '{:.3f}</td>'
        fmt0 += '</tr>'

        fmt1 = '<thead><tr>{0}</tr></thead><tbody>{1}</tbody>'
        html_tables = []
        nyrs = len(daily365[headers[0]])
        for yr in range(nyrs):
            tbody = ''
            ndoy = len(daily365[headers[0]][yr])
            for doy in range(ndoy):
                ndays = daily365['age'][yr][doy]
                nyrs = ndays / 365
                datalst = [(ndays, nyrs, daily365[k][yr][doy]) for k in headers]
                datalst = [item for sublist in datalst for item in sublist]
                tbody += fmt0.format(*datalst)
            html_tables.append(fmt1.format(thead, tbody))

        return html_tables
