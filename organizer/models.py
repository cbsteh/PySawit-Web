import os
import shutil
import uuid
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from weather.models import Weather
from .array import Array12ModelField, Array16ModelField
from .charts import Charts
from .outputsummary import OutputSummary
from .soillayer import SoilLayerModelField


class OPD(models.Model):
    class Meta:
        ordering = ['-updated_at']

    owner = models.ForeignKey(User,
                              blank=True,
                              null=True,
                              on_delete=models.CASCADE)

    slug = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    solarhour = models.CharField(max_length=10,
                                 default='12.0',
                                 editable=False)

    # 0. Control group:
    name = models.CharField(max_length=30,
                            blank=True,
                            verbose_name='Name of run',
                            help_text='Name this model run')
    nrun = models.CharField(max_length=10,
                            blank=True,
                            verbose_name='Simulation days',
                            help_text='(days): Number of simulation days',
                            default='7300')
    seed = models.CharField(max_length=15,
                            blank=True,
                            verbose_name='Seed',
                            help_text=('Seed for random number generator '
                                       '(-ve for random, +ve for deterministic)'),
                            default='965745566761')

    # 1. Meteorology group:
    lat = models.CharField(max_length=10,
                           blank=True,
                           verbose_name='Site latitude',
                           help_text='(deg.): Site latitude (+ve for North; -ve for South)',
                           default='2.253213')
    methgt = models.CharField(max_length=10,
                              blank=True,
                              verbose_name='Weather station height',
                              help_text='(m): Height from ground',
                              default='2.0')
    doy = models.CharField(max_length=10,
                           blank=True,
                           verbose_name='Initial day of year',
                           help_text='(day): Start of simulation (Jan. 1 = 1, ... Dec. 31 = 365',
                           default='1')
    dewtemp = models.CharField(max_length=10,
                               blank=True,
                               verbose_name='Dew point temperature',
                               help_text='(\u00b0C): Dew point air temperature',
                               default='23.0')
    lag = models.CharField(max_length=10,
                           blank=True,
                           verbose_name='No. of lag hours',
                           help_text=('(hours): No. of hours after sunrise when'
                                      ' air temperature is minimum'),
                           default='1.5')
    is_generated = models.CharField(max_length=1,
                                    verbose_name='Weather data source',
                                    help_text='Source of the daily weather data',
                                    choices=(('F', 'Use weather file'), ('S', 'Simulate weather')),
                                    default='S')
    weatherfilename = models.ForeignKey(Weather,
                                        blank=True,
                                        null=True,
                                        on_delete=models.CASCADE,   # weather files can be deleted
                                        related_name='opd',
                                        verbose_name='Weather filename',
                                        help_text='Filename of the daily weather data')

    # 1.1 Air temperature simulation:
    # 1.1.1 Min. air temperature:
    tmin_mean = models.CharField(max_length=10,
                                 blank=True,
                                 verbose_name='Annual average',
                                 help_text='(\u00b0C): Annual average of min. air temperature',
                                 default='23.823')
    tmin_amp = models.CharField(max_length=10,
                                blank=True,
                                verbose_name='Amplitude of average',
                                help_text=('(\u00b0C): Difference between the highest air '
                                           'temperature and the annual average min. air '
                                           'temperature'),
                                default='0.612')
    tmin_cv = models.CharField(max_length=10,
                               blank=True,
                               verbose_name='CV',
                               help_text=('(\u00b0C): Annual average monthly CV '
                                          '(coefficient of variation)'),
                               default='0.008')
    tmin_ampcv = models.CharField(max_length=10,
                                  blank=True,
                                  verbose_name='Amplitude of CV',
                                  help_text=('(\u00b0C): Difference between the lowest '
                                             'and annual average monthly CV'),
                                  default='-0.006')
    tmin_meanwet = models.CharField(max_length=10,
                                    blank=True,
                                    verbose_name='Annual average for wet days',
                                    help_text=('(\u00b0C): Annual average min. air '
                                               'temperature for only wet days'),
                                    default='23.823')

    # 1.1.2 Max. air temperature:
    tmax_mean = models.CharField(max_length=10,
                                 blank=True,
                                 verbose_name='Annual average',
                                 help_text='(\u00b0C): Annual average of max. air temperature',
                                 default='31.837')
    tmax_amp = models.CharField(max_length=10,
                                blank=True,
                                verbose_name='Amplitude of average',
                                help_text=('(\u00b0C): Difference between the highest air '
                                           'temperature and the annual average max. air '
                                           'temperature'),
                                default='0.798')
    tmax_cv = models.CharField(max_length=10,
                               blank=True,
                               verbose_name='CV',
                               help_text=('(\u00b0C): Annual average monthly CV '
                                          '(coefficient of variation)'),
                               default='0.009')
    tmax_ampcv = models.CharField(max_length=10,
                                  blank=True,
                                  verbose_name='Amplitude of CV',
                                  help_text=('(\u00b0C): Difference between the lowest '
                                             'and annual average monthly CV'),
                                  default='-0.007')
    tmax_meanwet = models.CharField(max_length=10,
                                    blank=True,
                                    verbose_name='Annual average for wet days',
                                    help_text=('(\u00b0C): Annual average max. air '
                                               'temperature for only wet days'),
                                    default='31.837')

    # 1.2 Rain simulation:
    # 1.2.1 Probability of rain:
    rain_pww = Array12ModelField(blank=True,
                                 verbose_name='P(W|W)',
                                 help_text=('^(0-1): Probability of having 2 wet (W) '
                                            'days in succession'),
                                 default=['Month', 'P(W|W)',
                                          'Jan', '0.64',
                                          'Feb', '0.45',
                                          'Mar', '0.49',
                                          'Apr', '0.46',
                                          'May', '0.50',
                                          'Jun', '0.54',
                                          'Jul', '0.51',
                                          'Aug', '0.55',
                                          'Sep', '0.60',
                                          'Oct', '0.71',
                                          'Nov', '0.82',
                                          'Dec', '0.80'],
                                 )
    rain_pwd = Array12ModelField(blank=True,
                                 verbose_name='P(W|D)',
                                 help_text=('^(0-1): Probability of having a '
                                            'dry (D) then wet (W) day'),
                                 default=['Month', 'P(W|D)',
                                          'Jan', '0.39',
                                          'Feb', '0.20',
                                          'Mar', '0.24',
                                          'Apr', '0.21',
                                          'May', '0.25',
                                          'Jun', '0.29',
                                          'Jul', '0.26',
                                          'Aug', '0.30',
                                          'Sep', '0.35',
                                          'Oct', '0.46',
                                          'Nov', '0.57',
                                          'Dec', '0.55'],
                                 )

    # 1.2.2 Gamma probability distribution:
    rain_shape = Array12ModelField(blank=True,
                                   verbose_name='Shape factor',
                                   help_text=('^(-): Shape factor \u03b1 of the gamma '
                                              'probability distribution'),
                                   default=['Month', '\u03b1',
                                            'Jan', '0.95'],
                                   )
    rain_scale = Array12ModelField(blank=True,
                                   verbose_name='Scale factor',
                                   help_text=('^(mm): Scale factor \u03b2 of the gamma '
                                              'probability distribution'),
                                   default=['Month', '\u03b2',
                                            'Jan', '16.39'],
                                   )

    # 1.3 Wind speed simulation:
    wind_shape = Array12ModelField(blank=True,
                                   verbose_name='Shape factor',
                                   help_text='^(-): Shape factor k of the Weibull distribution',
                                   default=['Month', 'k',
                                            'Jan', '1.595'],
                                   )
    wind_scale = Array12ModelField(blank=True,
                                   verbose_name='Scale factor',
                                   help_text=('^(m/s): Scale factor \u03bb of '
                                              'the Weibull distribution'),
                                   default=['Month', '\u03bb',
                                            'Jan', '2.578'],
                                   )

    # 2. Crop group:
    treeage = models.CharField(max_length=10,
                               blank=True,
                               verbose_name='Initial tree age',
                               help_text='(days): Tree/palm age at start of simulation',
                               default='365')
    plantdens = models.CharField(max_length=10,
                                 blank=True,
                                 verbose_name='Planting density',
                                 help_text='(palms/ha): No. of trees per ha',
                                 default='148')
    thinplantdens = models.CharField(max_length=10,
                                     blank=True,
                                     verbose_name='Thinning planting density',
                                     help_text=('(palms/ha): Planting density after thinning '
                                                '(-ve value for no thinning)'),
                                     default='-1')
    thinage = models.CharField(max_length=10,
                               blank=True,
                               verbose_name='Age of tree for thinning',
                               help_text=('(days): Age of tree for thinning '
                                          '(ignored if thinning planting density is -ve)'),
                               default='3650')
    femaleprob = models.CharField(max_length=10,
                                  blank=True,
                                  verbose_name='Probability of female flowers',
                                  help_text='(0-1): Probability of producing female flowers',
                                  default='0.5')

    # 2.1. Initial plant part dry weights:
    pinnae_wgt = models.CharField(max_length=10,
                                  blank=True,
                                  verbose_name='Pinnae weight',
                                  help_text='(kg/palm): Initial dry weight of pinnae',
                                  default='0.4')
    rachis_wgt = models.CharField(max_length=10,
                                  blank=True,
                                  verbose_name='Rachis weight',
                                  help_text='(kg/palm): Initial dry weight of rachis',
                                  default='0.7')
    trunk_wgt = models.CharField(max_length=10,
                                 blank=True,
                                 verbose_name='Trunk weight',
                                 help_text='(kg/palm): Initial dry weight of trunk',
                                 default='0.1')
    roots_wgt = models.CharField(max_length=10,
                                 blank=True,
                                 verbose_name='Roots weight',
                                 help_text='(kg/palm): Initial dry weight of roots',
                                 default='0.2')
    maleflo_wgt = models.CharField(max_length=10,
                                   blank=True,
                                   verbose_name='Male flowers weight',
                                   help_text='(kg/palm): Initial dry weight of male flowers',
                                   default='0.0')
    femaflo_wgt = models.CharField(max_length=10,
                                   blank=True,
                                   verbose_name='Female flowers weight',
                                   help_text='(kg/palm): Initial dry weight of female flowers',
                                   default='0.0')
    bunches_wgt = models.CharField(max_length=10,
                                   blank=True,
                                   verbose_name='Bunches weight',
                                   help_text='(kg/palm): Initial dry weight of bunches',
                                   default='0.0')

    # 2.2 Pinnae N and minerals content:
    pinnae_n = Array16ModelField(blank=True,
                                 verbose_name='Pinnae N',
                                 help_text='^N fraction in pinnae vs. palm age (days)',
                                 default=['Age', 'Fraction',
                                          '0', '0.026',
                                          '426', '0.0204',
                                          '883', '0.0182',
                                          '1218', '0.0196',
                                          '1583', '0.0202',
                                          '1948', '0.0188',
                                          '2313', '0.0211',
                                          '2739', '0.0193',
                                          '3135', '0.0198',
                                          '3500', '0.0208',
                                          '3866', '0.019',
                                          '4170', '0.0204',
                                          '4809', '0.0206',
                                          '5266', '0.0212',
                                          '5601', '0.0214',
                                          '11500', '0.02'],
                                 )
    pinnae_m = Array16ModelField(blank=True,
                                 verbose_name='Pinnae minerals',
                                 help_text='^Minerals fraction in pinnae vs. palm age (days)',
                                 default=['Age', 'Fraction',
                                          '0', '0.03917',
                                          '426', '0.02186',
                                          '883', '0.01854',
                                          '1218', '0.01862',
                                          '1583', '0.01753',
                                          '1948', '0.01805',
                                          '2313', '0.01719',
                                          '2739', '0.01628',
                                          '3135', '0.01643',
                                          '3500', '0.016',
                                          '3866', '0.0172',
                                          '4170', '0.01564',
                                          '4809', '0.01597',
                                          '5266', '0.01603',
                                          '5601', '0.01486',
                                          '11500', '0.015'],
                                 )

    # 2.3 Rachis N and minerals content:
    rachis_n = Array16ModelField(blank=True,
                                 verbose_name='Rachis N',
                                 help_text='^N fraction in rachis vs. palm age (days)',
                                 default=['Age', 'Fraction',
                                          '0', '0.0059',
                                          '426', '0.00423',
                                          '883', '0.00421',
                                          '1218', '0.00383',
                                          '1583', '0.0035',
                                          '1948', '0.00335',
                                          '2313', '0.00325',
                                          '2739', '0.00383',
                                          '3135', '0.00361',
                                          '3500', '0.00292',
                                          '3866', '0.00346',
                                          '4170', '0.0034',
                                          '4809', '0.00368',
                                          '5266', '0.00426',
                                          '5601', '0.00448',
                                          '11500', '0.00448'],
                                 )
    rachis_m = Array16ModelField(blank=True,
                                 verbose_name='Rachis minerals',
                                 help_text='^Minerals fraction in rachis vs. palm age (days)',
                                 default=['Age', 'Fraction',
                                          '0', '0.01854',
                                          '426', '0.01399',
                                          '883', '0.01721',
                                          '1218', '0.02072',
                                          '1583', '0.01722',
                                          '1948', '0.02082',
                                          '2313', '0.01939',
                                          '2739', '0.01501',
                                          '3135', '0.01808',
                                          '3500', '0.01829',
                                          '3866', '0.02032',
                                          '4170', '0.01503',
                                          '4809', '0.01503',
                                          '5266', '0.01503',
                                          '5601', '0.01595',
                                          '11500', '0.0177'],
                                 )

    # 2.4 Roots N and minerals content:
    roots_n = Array16ModelField(blank=True,
                                verbose_name='Roots N',
                                help_text='^N fraction in roots vs. palm age (days)',
                                default=['Age', 'Fraction',
                                         '0', '0.0107',
                                         '883', '0.00498',
                                         '2313', '0.00326',
                                         '3866', '0.00342',
                                         '5266', '0.00285',
                                         '11500', '0.002'],
                                )
    roots_m = Array16ModelField(blank=True,
                                verbose_name='Roots minerals',
                                help_text='^Minerals fraction in roots vs. palm age (days)',
                                default=['Age', 'Fraction',
                                         '0', '0.021',
                                         '883', '0.0157',
                                         '2313', '0.0133',
                                         '3866', '0.0124',
                                         '5266', '0.0231',
                                         '11500', '0.02'],
                                )

    # 2.5 Rachis N and minerals content:
    trunk_n = Array16ModelField(blank=True,
                                verbose_name='Trunk N',
                                help_text='^N fraction in trunk vs. palm age (days)',
                                default=['Age', 'Fraction',
                                         '0', '0.0101',
                                         '426', '0.00707',
                                         '883', '0.00955',
                                         '1218', '0.00825',
                                         '1583', '0.00685',
                                         '1948', '0.00742',
                                         '2313', '0.00574',
                                         '2739', '0.0071',
                                         '3135', '0.00753',
                                         '3500', '0.00509',
                                         '3866', '0.00459',
                                         '4170', '0.00631',
                                         '4809', '0.0048',
                                         '5266', '0.00483',
                                         '5601', '0.00492',
                                         '11500', '0.004'],
                                )
    trunk_m = Array16ModelField(blank=True,
                                verbose_name='Trunk minerals',
                                help_text='^Minerals fraction in trunk vs. palm age (days)',
                                default=['Age', 'Fraction',
                                         '0', '0.0176',
                                         '426', '0.0166',
                                         '883', '0.0308',
                                         '1218', '0.0351',
                                         '1583', '0.0349',
                                         '1948', '0.0351',
                                         '2313', '0.0285',
                                         '2739', '0.0259',
                                         '3135', '0.0231',
                                         '3500', '0.0232',
                                         '3866', '0.0285',
                                         '4170', '0.0172',
                                         '4809', '0.028',
                                         '5266', '0.0238',
                                         '5601', '0.0156',
                                         '11500', '0.015'],
                                )

    # 2.6 Specific leaf area (SLA):
    sla = Array16ModelField(blank=True,
                            verbose_name='SLA',
                            help_text='^Specific leaf area (SLA) (m2/kg) vs. palm age (days)',
                            default=['Age', 'SLA',
                                     '0', '13.20',
                                     '365', '13.20',
                                     '840', '7.25',
                                     '4234', '7.25',
                                     '6169', '7.25',
                                     '7300', '7.25',
                                     '11500', '7.25'],
                            )

    # 3. Energy balance:
    co2ambient = models.CharField(max_length=10,
                                  blank=True,
                                  verbose_name='Initial ambient CO2',
                                  help_text=('(\u00b5mol/mol or year): Atmospheric concentration '
                                             'of CO2 (+ve for actual value or -ve for year)'),
                                  default='-1987')
    co2change = models.CharField(max_length=10,
                                 blank=True,
                                 verbose_name='Change in ambient CO2',
                                 help_text=('(\u00b5mol/mol/yr): Annual change in atmospheric '
                                            'CO2 concentration'),
                                 default='1.7')
    refhgt = models.CharField(max_length=10,
                              blank=True,
                              verbose_name='Reference height',
                              help_text='(m): Height from ground',
                              default='23.0')

    # 4. Soil water
    numintervals = models.CharField(max_length=10,
                                    blank=True,
                                    verbose_name='No of subintervals',
                                    help_text=('No. of subintervals in a day '
                                               'for daily integration'),
                                    default='100')
    rootdepth = models.CharField(max_length=10,
                                 blank=True,
                                 verbose_name='Initial rooting depth',
                                 help_text='(m): Depth of roots below the soil surface',
                                 default='0.2')
    has_watertable = models.CharField(max_length=1,
                                      verbose_name='Any water table?',
                                      help_text=('Select "Yes" if there is a water table and it '
                                                 'is just below the last soil layer'),
                                      choices=(('Y', 'Yes'), ('N', 'No')),
                                      default='N')
    numlayers = models.CharField(max_length=1,
                                 verbose_name='No. of soil layers',
                                 help_text='Min: 2 layers, Max: 6 layers',
                                 choices=(('2', '2'),
                                          ('3', '3'),
                                          ('4', '4'),
                                          ('5', '5'),
                                          ('6', '6')),
                                 default='3')

    # 4.1 Soil layer 1:
    layer1 = SoilLayerModelField(blank=True,
                                 verbose_name='Soil Layer 1',
                                 help_text='^Soil properties',
                                 default=['0.05',
                                          '-2',
                                          '25.0',
                                          '70.0',
                                          '2.0'],
                                 )

    # 4.2 Soil layer 2:
    layer2 = SoilLayerModelField(blank=True,
                                 verbose_name='Soil Layer 2',
                                 help_text='^Soil properties',
                                 default=['0.55',
                                          '-2',
                                          '29.0',
                                          '66.0',
                                          '1.5'],
                                 )

    # 4.3 Soil layer 3:
    layer3 = SoilLayerModelField(blank=True,
                                 verbose_name='Soil Layer 3',
                                 help_text='^Soil properties',
                                 default=['0.90',
                                          '-2',
                                          '29.0',
                                          '66.0',
                                          '0.0'],
                                 )

    # 4.4 Soil layer 4:
    layer4 = SoilLayerModelField(blank=True,
                                 verbose_name='Soil Layer 4',
                                 help_text='^Soil properties',
                                 default=['0.25',
                                          '-2',
                                          '50.0',
                                          '25.0',
                                          '0.0'],
                                 )

    # 4.5 Soil layer 5:
    layer5 = SoilLayerModelField(blank=True,
                                 verbose_name='Soil Layer 5',
                                 help_text='^Soil properties',
                                 default=['0.25',
                                          '-2',
                                          '50.0',
                                          '25.0',
                                          '0.0'],
                                 )

    # 4.6 Soil layer 6:
    layer6 = SoilLayerModelField(blank=True,
                                 verbose_name='Soil Layer 6',
                                 help_text='^Soil properties',
                                 default=['0.25',
                                          '-2',
                                          '50.0',
                                          '25.0',
                                          '0.0'],
                                 )

    def __str__(self):
        return self.name

    def pprint_ini(self):
        def del_last_comma(s):
            idx = s.rfind(',')
            s = s[:idx] + s[idx + 1:]
            return s

        def level0(template0, lst0, s):
            for field in lst0:
                s += template0.format('\t', field, dct[field])
            return s

        def level1a(template0, template1, lst0, grouptitle, s):
            txt0 = ''
            for field in lst0:
                arr_lst = field[1].split(',')[3::2]
                arr_str = '[{0}]'.format(', '.join(l for l in arr_lst if l))
                txt0 += template0.format('\t' * 2, field[0], arr_str)
            s += template1.format('\t', grouptitle, del_last_comma(txt0))
            return s

        def level1b(template0, template1, lst0, grouptitle, s):
            txt0 = ''
            for field in lst0:
                txt0 += template0.format('\t' * 2, field[0], field[1])
            s += template1.format('\t', grouptitle, del_last_comma(txt0))
            return s

        def level1c(template0, template1, lst0, s):
            for field in lst0:
                txt0 = ''
                arr_lst = field[1].split(',')[2:]
                xys = [(v1, v2) for v1, v2 in zip(arr_lst[::2], arr_lst[1::2]) if v1 and v2]
                for xy in xys:
                    txt0 += template0.format('\t' * 2, xy[0], xy[1])
                s += template1.format('\t', field[0], del_last_comma(txt0))
            return s

        def level_layer(lyr):
            template = ('\n\t\t{{\n'
                        '\t\t\t"thick": {0},\n'
                        '\t\t\t"vwc": {1},\n'
                        '\t\t\t"texture": {{\n'
                        '\t\t\t\t"clay": {2},\n'
                        '\t\t\t\t"sand": {3},\n'
                        '\t\t\t\t"om": {4}\n'
                        '\t\t\t}}\n'
                        '\t\t}},')
            lst0 = lyr.split(',')
            return template.format(*lst0)

        dct = {}
        dct.update([(k, v) for k, v in self.__dict__.items() if not k.startswith('_')])

        t0 = '{0}"{1}": {2},\n'
        t1 = '{0}"{1}": {{\n{2}{0}}},\n'
        ini = ''

        # 1. METEOROLOGY:
        lst = ['seed', 'lat', 'methgt', 'doy', 'solarhour', 'dewtemp', 'lag']
        ini = level0(t0, lst, ini)

        k = 'is_generated'
        ini += t0.format('\t', k, 'true' if dct[k] == 'S' else 'false')
        k = 'weatherfilename'
        if self.weatherfilename:
            fname = self.weatherpath() + self.weatherfilename.name
            fname = fname.replace('\\', '/')
        else:
            fname = ''
        ini += t0.format('\t', k, '"{0}"'.format(fname))

        lst = [('pww', self.rain_pww), ('pwd', self.rain_pwd),
               ('shape', self.rain_shape), ('scale', self.rain_scale)]
        ini = level1a(t0, t1, lst, 'rain', ini)

        lst = [('mean', self.tmin_mean), ('amp', self.tmin_amp),
               ('cv', self.tmin_cv), ('ampcv', self.tmin_ampcv),
               ('meanwet', self.tmin_meanwet)]
        ini = level1b(t0, t1, lst, 'tmin', ini)

        lst = [('mean', self.tmax_mean), ('amp', self.tmax_amp),
               ('cv', self.tmax_cv), ('ampcv', self.tmax_ampcv),
               ('meanwet', self.tmax_meanwet)]
        ini = level1b(t0, t1, lst, 'tmax', ini)

        lst = [('shape', self.wind_shape), ('scale', self.wind_scale)]
        ini = level1a(t0, t1, lst, 'wind', ini)

        # 2. ENERGY BALANCE:
        lst = ['co2ambient', 'co2change', 'refhgt']
        ini = level0(t0, lst, ini)

        # 3. SOIL WATER:
        lst = ['numintervals', 'rootdepth', 'numlayers']
        ini = level0(t0, lst, ini)
        k = 'has_watertable'
        ini += t0.format('\t', k, 'true' if dct[k] == 'Y' else 'false')

        txt = ''
        lst = [self.layer1, self.layer2, self.layer3, self.layer4, self.layer5, self.layer6]
        for layer in lst:
            txt += level_layer(layer)
        ini += '\t"layers": [{0}\n\t],\n'.format(del_last_comma(txt))

        # 4. CROP:
        lst = ['treeage', 'plantdens', 'thinplantdens', 'thinage', 'femaleprob', 'pinnae_wgt',
               'rachis_wgt', 'trunk_wgt', 'roots_wgt', 'maleflo_wgt', 'femaflo_wgt', 'bunches_wgt']
        ini = level0(t0, lst, ini)

        lst = [('sla', self.sla),
               ('pinnae_n', self.pinnae_n), ('pinnae_m', self.pinnae_m),
               ('rachis_n', self.rachis_n), ('rachis_m', self.rachis_m),
               ('roots_n', self.roots_n), ('roots_m', self.roots_m),
               ('trunk_n', self.trunk_n), ('trunk_m', self.trunk_m)]
        ini = level1c(t0, t1, lst, ini)

        ini = '{{\n{0}}}\n'.format(del_last_comma(ini))

        fullpath = self.inifile()
        with open(fullpath, 'wt') as fout:
            fout.write(ini)
        return fullpath

    def weatherpath(self):
        directory = '{0}/user_{1}/weather/'.format(settings.MEDIA_ROOT, self.owner.id)
        return directory.replace('\\', '/')

    def reqpath(self):
        directory = '{0}/requests/user_{1}/{2}/'.format(settings.MEDIA_ROOT,
                                                        self.owner.id, str(self.slug))
        return directory.replace('\\', '/')

    def get_req_path(self, filename, must_exist=False):
        directory = self.reqpath()
        if not os.path.exists(directory):
            if not must_exist:
                os.makedirs(directory)
            else:
                return ''
        fullpath = directory + filename
        if must_exist and not os.path.isfile(fullpath):
            fullpath = ''
        return fullpath

    def runpath(self):
        directory = '{0}/user_{1}/runs/{2}/'.format(settings.MEDIA_ROOT,
                                                    self.owner.id, str(self.slug))
        return directory.replace('\\', '/')

    def get_run_path(self, filename, must_exist=False):
        directory = self.runpath()
        if not os.path.exists(directory):
            if not must_exist:
                os.makedirs(directory)
            else:
                return ''
        fullpath = directory + filename
        if must_exist and not os.path.isfile(fullpath):
            fullpath = ''
        return fullpath

    def has_request(self):
        return os.path.exists(self.reqpath())

    def has_error(self):
        fullpath = self.get_run_path('error.txt', must_exist=True)
        return fullpath != ''

    def delete_run(self):
        shutil.rmtree(self.runpath(), ignore_errors=True)

    def delete_request(self):
        shutil.rmtree(self.reqpath(), ignore_errors=True)

    def errfile(self, must_exist=False):
        return self.get_run_path('error.txt', must_exist)

    def inifile(self, must_exist=False):
        return self.get_run_path('ini.txt', must_exist)

    def outfile(self, must_exist=False):
        return self.get_run_path('day.txt', must_exist)

    def annfile(self, must_exist=False):
        return self.get_run_path('ann.txt', must_exist)

    def reqfile(self, must_exist=False):
        return self.get_req_path('req.txt', must_exist)

    def lockfile(self, must_exist=False):
        return self.get_run_path('lock.txt', must_exist)

    def picklefile(self, must_exist=False):
        return self.get_run_path('tables365.pickle', must_exist)

    def view_input_results(self):
        infile = self.inifile(True)
        if infile:
            with open(infile, 'r') as fin:
                content = fin.read()
        else:
            content = 'No input file found.'
        return content

    def create_annual_results(self):
        dayfile = self.outfile(True)
        outsum = OutputSummary(dayfile, int(self.plantdens), int(self.numlayers))
        outsum.summarize()
        annfile = self.annfile()
        outsum.annual_as_file(annfile)

    def view_annual_results(self):
        dayfile = self.outfile(True)
        if dayfile:
            outsum = OutputSummary(dayfile, int(self.plantdens), int(self.numlayers))
            outsum.summarize()
            annfile = self.annfile()
            outsum.annual_as_file(annfile)
            html = ('<div class="table-div">'
                    '<table class="Table">{0}</table></div>')
            content = html.format(outsum.annual_as_table())
        else:
            content = '<p>No model results found.</p>'
        return content

    def request_run(self):
        self.delete_run()
        slug = str(self.slug)
        ini = self.pprint_ini()
        out = self.outfile()
        req = self.reqfile()
        with open(req, 'w') as fout:
            fout.write(ini + '\n')
            fout.write(out + '\n')
            fout.write(self.nrun + '\n')
            fout.write(slug + '\n')
            fout.write(self.name + '\n')
            fout.write(datetime.now().strftime('%b. %d, %Y, %H:%M') + '\n')

    def create_annual_charts(self):
        figures = []
        dayfile = self.outfile(True)
        if dayfile:
            outsum = OutputSummary(dayfile, int(self.plantdens), int(self.numlayers))
            outsum.summarize()
            annfile = self.annfile()
            outsum.annual_as_file(annfile)
            cht = Charts(int(self.treeage), outsum.daily, outsum.annual)
            figures = cht.plot_all(annual=True)
        return figures

    def create_daily_charts(self):
        figures = []
        dayfile = self.outfile(True)
        if dayfile:
            outsum = OutputSummary(dayfile, int(self.plantdens), int(self.numlayers))
            outsum.summarize()
            annfile = self.annfile()
            outsum.annual_as_file(annfile)
            cht = Charts(int(self.treeage), outsum.daily, outsum.annual)
            figures = cht.plot_all(annual=False)
        return figures

    def get_plot_parameters(self, annual):
        dayfile = self.outfile(True)
        params = []
        if dayfile:
            outsum = OutputSummary(dayfile, int(self.plantdens), int(self.numlayers))
            outsum.summarize()
            dct = outsum.annual if annual else outsum.daily
            params = [key for key in dct.keys()]
        return params

    def plot_batch(self, x, ylst, annual, chart_type):
        figure = []
        dayfile = self.outfile(True)
        if dayfile:
            outsum = OutputSummary(dayfile, int(self.plantdens), int(self.numlayers))
            outsum.summarize()
            annfile = self.annfile()
            outsum.annual_as_file(annfile)
            cht = Charts(int(self.treeage), outsum.daily, outsum.annual)
            dct = outsum.annual if annual else outsum.daily
            paramx = dct[x]
            paramy = [dct[y] for y in ylst]
            if len(ylst) > 1:
                axis_ylabel = ', '.join(ylst)
                caption = '({}) vs. {}'.format(axis_ylabel, x)
            else:
                axis_ylabel = ylst[0]
                caption = '{} vs. {}'.format(axis_ylabel, x)

            figure = cht.plot_batch(paramx,
                                    paramy, ylst,
                                    x, axis_ylabel,
                                    caption, True,
                                    chart_type)
        return figure

    def get_absolute_url(self):
        return reverse('organizer_opd_detail', kwargs={'slug': self.slug})

    def get_delete_url(self):
        return reverse('organizer_opd_delete', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('organizer_opd_update', kwargs={'slug': self.slug})

    def get_copy_url(self):
        return reverse('organizer_opd_copy', kwargs={'slug': self.slug})

    def get_confirm_run_url(self):
        return reverse('organizer_opd_confirm_run', kwargs={'slug': self.slug})

    def get_request_run_url(self):
        return reverse('organizer_opd_request_run', kwargs={'slug': self.slug})

    def get_results_url(self):
        return reverse('organizer_opd_results', kwargs={'slug': self.slug})

    def get_results_annual_url(self):
        return reverse('organizer_opd_results_annual', kwargs={'slug': self.slug})

    def get_results_annual_charts_url(self):
        return reverse('organizer_opd_results_annual_charts', kwargs={'slug': self.slug})

    def get_results_daily_charts_url(self):
        return reverse('organizer_opd_results_daily_charts', kwargs={'slug': self.slug})

    def get_results_daily_plot_url(self):
        return reverse('organizer_opd_results_daily_plot', kwargs={'slug': self.slug})

    def get_results_annual_plot_url(self):
        return reverse('organizer_opd_results_annual_plot', kwargs={'slug': self.slug})

    def get_download_annual_url(self):
        return reverse('organizer_opd_download_annual', kwargs={'slug': self.slug})

    def get_results_daily_url(self):
        return reverse('organizer_opd_results_daily', kwargs={'slug': self.slug})

    def get_download_daily_url(self):
        return reverse('organizer_opd_download_daily', kwargs={'slug': self.slug})

    def get_results_input_url(self):
        return reverse('organizer_opd_results_input', kwargs={'slug': self.slug})

    def get_download_input_url(self):
        return reverse('organizer_opd_download_input', kwargs={'slug': self.slug})
