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
    pickup_distribution = OrderedDict()

    current_lat = '40.730610'
    current_long = '-73.935242'

    if request.method == 'POST':

        #Updates the lat and long
        current_lat = request.POST.get('pick_up_lat', '40.730610')
        current_long = request.POST.get('pick_up_lon',  '-73.935242')
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
        print "Number of dropoffs", len(drop_offs)

        dropoffs_df = pd.DataFrame(drop_offs)
        dropoffs_df.to_csv("test_grouping.csv", encoding="utf-8")
        hour_grouped = dropoffs_df.set_index('pickup_datetime').groupby(pd.TimeGrouper('1h'))

        print hour_grouped

        #for index in hour_grouped:
        #    print index


        hour_range = pd.date_range('00:00:00', periods=24, freq='H')

        for hour in hour_range:
            hour_string = hour.strftime("%H:%M")
            pickup_distribution[hour_string] = 10

        print pickup_distribution


    context = RequestContext(request, {
        'drop_offs': drop_offs,
        'current_lat': Decimal(current_lat),
        'current_long': Decimal(current_long),
        'pickup_distribution': pickup_distribution,
    })
    return render(request, 'taxis/google_map.html', context)