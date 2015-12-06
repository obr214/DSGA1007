from collections import OrderedDict
from decimal import Decimal
from django.db import connection
from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from taxis.models import TaxiPickUps
from functions import get_cluster_list, get_dropoffs_df_from_db, format_date

import pandas as pd



def google_map(request):
    error_message = None
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
        pickup_date = request.POST.get('pickup_date', '01/01/2015')

        pickup_date_init, pickup_date_end = format_date(pickup_date)

        drop_offs = get_dropoffs_df_from_db(current_lat, current_long, pickup_date_init, pickup_date_end)
        number_dropoffs = len(drop_offs)
        print "Number of dropoffs", len(drop_offs)

        dropoffs_df = pd.DataFrame(drop_offs)

        try:

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

        except LookupError:
            print "Error"
            results_flag = False
            error_message = 'There is no data for this day or this location. Please try another another combination'

    context = RequestContext(request, {
        'drop_offs': drop_offs,
        'current_lat': Decimal(current_lat),
        'current_long': Decimal(current_long),
        'results_flag': results_flag,
        'number_dropoffs': number_dropoffs,
        'pickup_distribution': pickup_distribution,
        'rate_summary': rate_summary,
        'distance_summary': distance_summary,
        'error': error_message,
    })
    return render(request, 'taxis/google_map.html', context)


def test_coordinates(request):
    print "Test Coordinates"
    drop_offs = None
    results_flag = False
    number_dropoffs = None
    cluster_list = None

    current_lat = '40.730610'
    current_long = '-73.935242'

    if request.method == 'POST':
        results_flag = True

        #Updates the lat and long
        current_lat = request.POST.get('pick_up_lat', '40.730610')
        current_long = request.POST.get('pick_up_lon',  '-73.935242')
        pickup_date = request.POST.get('pickup_date', '01/01/2015')

        pickup_date_init, pickup_date_end = format_date(pickup_date)

        drop_offs = get_dropoffs_df_from_db(current_lat, current_long, pickup_date_init, pickup_date_end)
        number_dropoffs = len(drop_offs)
        print "Number of dropoffs", len(drop_offs)

        dropoffs_df = pd.DataFrame(drop_offs)

        cluster_list = get_cluster_list(dropoffs_df)

    context = RequestContext(request, {
        'drop_offs': drop_offs,
        'current_lat': Decimal(current_lat),
        'current_long': Decimal(current_long),
        'results_flag': results_flag,
        'number_dropoffs': number_dropoffs,
        'cluster_list': cluster_list,
    })
    return render(request, 'taxis/coordinates_test.html', context)