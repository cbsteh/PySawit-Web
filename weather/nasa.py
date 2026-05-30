import json
import math
import shutil
import tempfile
import urllib.request

from collections import OrderedDict


class NASAData:
    TMIN = 'T2M_MIN'
    TMAX = 'T2M_MAX'
    WIND = 'WS2M'
    RAIN = 'PRECTOT'

    # default values to use for missing data (NASA code -99):
    default_tmin = 22.0
    default_tmax = 33.0
    default_wind = 1.0
    default_rain = 0.0

    def __init__(self, params):
        self.data = None
        self.status = None
        self.create_weather_file(params)

    def get_nasa_data(self, params):
        url = ('https://power.larc.nasa.gov/cgi-bin/v1/DataAccess.py?'
               'request=execute&'
               'identifier=SinglePoint&'
               'parameters={tmin},{tmax},{wind},{rain}&'
               'startDate={startdate}&'
               'endDate={enddate}&'
               'userCommunity=AG&'
               'tempAverage=DAILY&'
               'outputList=CSV&'
               'lat={lat}&'
               'lon={lon}&'
               'user=anonymous').format(tmin=NASAData.TMIN,
                                        tmax=NASAData.TMAX,
                                        wind=NASAData.WIND,
                                        rain=NASAData.RAIN,
                                        startdate=params['start_date'],
                                        enddate=params['end_date'],
                                        lat=params['lat'],
                                        lon=params['lon'])
        tf = tempfile.NamedTemporaryFile()
        with urllib.request.urlopen(url) as response:
            shutil.copyfileobj(response, tf)
        tf.seek(0)
        self.data = json.loads(tf.read())

    def is_valid(self):
        msg = self.data['messages']
        if not msg:
            ret = [True, 'No error']
        else:
            ret = [False, msg[0]['Alert']['Description']['Issue']]
        return ret

    def create_weather_file(self, params):
        self.get_nasa_data(params)
        self.status = self.is_valid()

        if self.status[0]:
            # stored dates in the dictionary must be ordered/sorted:
            parameter = self.data['features'][0]['properties']['parameter']
            fields = [NASAData.TMIN, NASAData.TMAX, NASAData.WIND, NASAData.RAIN]
            for field in fields:
                dct = parameter[field]
                parameter[field] = OrderedDict([(key, dct[key]) for key in sorted(dct.keys())])

            is_calibrate = params['calibrate_check']
            if is_calibrate:
                self.calib_tmin()
                self.calib_tmax()
                self.calib_wind()
                self.calib_rain()

            weather_filename = params['weather_filename']
            with open(weather_filename, 'wt') as fout:
                coord = self.data['features'][0]['geometry']['coordinates']
                lon = coord[0]
                lat = coord[1]
                elev = coord[2]
                date = self.data['header']['startDate']
                startdate = date[0:4] + '/' + date[4:6] + '/' + date[6:]
                date = self.data['header']['endDate']
                enddate = date[0:4] + '/' + date[4:6] + '/' + date[6:]
                fout.write(('# GPS: {}, {} deg., '
                            'Elev: {} m, Station: 2 m\n').format(lat, lon, elev))
                fout.write('# {} - {}\n'.format(startdate, enddate))

                strftmt = ('{},' * 5)[:-1] + '\n'
                fout.write(strftmt.format('*doy', 'tmin', 'tmax', 'wind', 'rain'))
                defvals = [NASAData.default_tmin, NASAData.default_tmax,
                           NASAData.default_wind, NASAData.default_rain]
                strftmt = '{},' + ('{:.3f},' * 4)[:-1] + '\n'
                for doy, data in enumerate(zip(self.tmin().values(),
                                               self.tmax().values(),
                                               self.wind().values(),
                                               self.rain().values())):
                    vals = []
                    for i, defval in enumerate(defvals):
                        vals.append(NASAData.treat_missing_value(data[i], defval))
                    fout.write(strftmt.format((doy % 365) + 1, *vals))
        return self.status

    @staticmethod
    def treat_missing_value(val, default_val):
        return val if val > -98.9 else default_val

    def calib_tmin(self):
        tmin = self.tmin()
        coord = self.data['features'][0]['geometry']['coordinates']
        lat = coord[1]
        a = 0.142 + 1.799 * math.exp(-lat)
        for key, val in tmin.items():
            if val != '-99':
                val = float(val)
                val = 23.744 - a * (25.324 - val)
                tmin[key] = val

    def calib_tmax(self):
        tmax = self.tmax()
        coord = self.data['features'][0]['geometry']['coordinates']
        lon = coord[0]
        lat = coord[1]

        for i, key in enumerate(sorted(tmax.keys())):
            if tmax[key] != '-99':
                val = float(tmax[key])
                doy = (i % 365) + 1
                val = 13.595 + 0.69 * val - 0.018 * lon + 0.575 * lat - 0.003 * doy
                tmax[key] = val

    def calib_wind(self):
        wind = self.wind()
        for key, val in wind.items():
            if val != '-99':
                val = float(val)
                val = 1.2096 * math.exp(0.2012 * val)
                wind[key] = val

    def calib_rain(self):
        rain = self.rain()
        coord = self.data['features'][0]['geometry']['coordinates']
        lat = coord[1]
        date = self.data['header']['startDate']
        year = int(date[0:4])

        annualrain = []
        uncalib_total = 0.0
        ndays = 0
        nwet = 0
        for i, key in enumerate(rain.keys()):
            val = rain[key]
            if val != '-99':
                val = float(val)
                val = val if val > 4.0 else 0.0
                rain[key] = val
                uncalib_total += val
                ndays += 1
                if val > 0:
                    nwet += 1

                if (i + 1) % 365 == 0:
                    annualrain.append([uncalib_total, ndays, nwet, 0.0])
                    uncalib_total = 0.0
                    ndays = 0
                    nwet = 0
            else:
                rain[key] = -99

        for i, vals in enumerate(annualrain):
            uncalib_total = vals[0]
            ndays = vals[1]
            nwet = vals[2]
            tot = uncalib_total / ndays * 365
            calib_total = 27160.195 + 1.195 * tot - 13.647 * (year + i) + 44.673 * lat
            annualrain[i][3] = (calib_total - uncalib_total) / nwet

        numyrs = len(annualrain)
        for i, key in enumerate(rain.keys()):
            val = rain[key]
            if val > 0.0:
                yr = min(int(i / 365), numyrs-1)
                rain[key] += annualrain[yr][3]

    def tmin(self):
        parameter = self.data['features'][0]['properties']['parameter']
        return parameter[NASAData.TMIN]

    def tmax(self):
        parameter = self.data['features'][0]['properties']['parameter']
        return parameter[NASAData.TMAX]

    def wind(self):
        parameter = self.data['features'][0]['properties']['parameter']
        return parameter[NASAData.WIND]

    def rain(self):
        parameter = self.data['features'][0]['properties']['parameter']
        return parameter[NASAData.RAIN]
