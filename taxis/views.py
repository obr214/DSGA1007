from collections import OrderedDict
from decimal import Decimal
from django.db import connection
from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from taxis.models import TaxiPickUps

import pandas as pd

def dictfetchall(cursor):
    #Return all rows from a cursor as a dict
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def google_map(request):
    drop_offs = None
    results_flag = False
    number_dropoffs = None
    pickup_distribution = OrderedDict()
    rate_summary = OrderedDict()
    distance_summary = OrderedDict()

    current_lat = '40.730610'
    current_long = '-73.935242'

    if request.method == 'POST':
        results_flag = True

        #Updates the lat and long
        current_lat = request.POST.get('pick_up_lat', '40.730610')
        current_long = request.POST.get('pick_up_lon',  '-73.935242')
        print current_lat, current_long
        #pickup_date = request.POST.get('pickup_date', '2015-01-01')
        pickup_date = '2015-01-01'
        pickup_date_init = pickup_date + ' 00:00:00'
        pickup_date_end = pickup_date + ' 23:59:59'

        cursor = connection.cursor()

        cursor.execute('SELECT *, '
                       '(3959 * acos (cos ( radians(%s) )'
                       '* cos( radians( pickup_latitude ) )'
                       '* cos( radians( pickup_longitude ) '
                       '- radians( %s ) ) '
                       '+ sin ( radians( %s) )'
                       '* sin( radians( pickup_latitude ) )'
                       ')'
                       ') AS distance '
                       'FROM taxis_taxipickups '
                       'HAVING distance < 0.0621371 '
                       'AND pickup_datetime BETWEEN CAST(%s AS DATETIME) AND CAST(%s as DATETIME) '
                       'ORDER BY pickup_datetime',
                       [current_lat, current_long, current_lat, pickup_date_init, pickup_date_end]
                       )

        drop_offs = dictfetchall(cursor)
        number_dropoffs = len(drop_offs)
        print "Number of dropoffs", len(drop_offs)

        dropoffs_df = pd.DataFrame(drop_offs)

        #hour_grouped = dropoffs_df.set_index('pickup_datetime').groupby(pd.TimeGrouper('1h'))

        #print hour_grouped

        hour_range = pd.date_range('00:00:00', periods=24, freq='H')

        for hour in hour_range:
            hour_string = hour.strftime("%H:%M")
            pickup_distribution[hour_string] = 0

        dropoffs_df['pickup_datetime'] = pd.to_datetime(dropoffs_df['pickup_datetime'])
        times = pd.DatetimeIndex(dropoffs_df.pickup_datetime)

        hour_groups = dropoffs_df.groupby([times.hour]).size()
        for hg in hour_groups.index:
            #Leading zeros
            hour_string = str(hg).zfill(2)+':00'
            pickup_distribution[hour_string] = int(hour_groups[hg])


        #Get the descriptive summary
        rate_sum_statistics = dropoffs_df['total_amount'].describe()
        rate_summary['Mean'] = rate_sum_statistics['mean']
        rate_summary['Std Dev'] = rate_sum_statistics['std']
        rate_summary['25%'] = rate_sum_statistics['25%']
        rate_summary['50%'] = rate_sum_statistics['50%']
        rate_summary['75%'] = rate_sum_statistics['75%']
        rate_summary['Max'] = rate_sum_statistics['max']

        distance_sum_statistics = dropoffs_df['trip_distance'].describe()
        distance_summary['Mean'] = distance_sum_statistics['mean']
        distance_summary['Std Dev'] = distance_sum_statistics['std']
        distance_summary['25%'] = distance_sum_statistics['25%']
        distance_summary['50%'] = distance_sum_statistics['50%']
        distance_summary['75%'] = distance_sum_statistics['75%']
        distance_summary['Max'] = distance_sum_statistics['max']


    context = RequestContext(request, {
        'drop_offs': drop_offs,
        'current_lat': Decimal(current_lat),
        'current_long': Decimal(current_long),
        'results_flag': results_flag,
        'number_dropoffs': number_dropoffs,
        'pickup_distribution': pickup_distribution,
        'rate_summary': rate_summary,
        'distance_summary': distance_summary,
    })
    return render(request, 'taxis/google_map.html', context)