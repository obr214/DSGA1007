from collections import OrderedDict
from decimal import Decimal
from django.db import connection
from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from taxis.models import TaxiPickUps
from functions import get_cluster_list, get_dropoffs_df_from_db, format_date, get_cluster_listthing
from taxi_analyzer import TaxiAnalyzer


import pandas as pd


def google_map(request):
    original_date = ''
    error_message = None
    drop_offs = None
    results_flag = False
    number_dropoffs = None
    cluster_list = None
    pickup_distribution = None
    rate_summary = None
    distance_summary = None

    current_lat = '40.730610'
    current_long = '-73.935242'

    if request.method == 'POST':
        results_flag = True

        #Updates the lat and long
        current_lat = request.POST.get('pick_up_lat', '40.730610')
        current_long = request.POST.get('pick_up_lon',  '-73.935242')
        pickup_date = request.POST.get('pickup_date', '01/01/2015')
        original_date = 'pickup_date'

        taxi_analyzer = TaxiAnalyzer()
        taxi_analyzer.get_data(pickup_date, current_long, current_lat)
        drop_offs = taxi_analyzer.get_dropoffs()
        number_dropoffs = taxi_analyzer.get_size()


        try:
            cluster_list = taxi_analyzer.get_top_clusters(20)

            pickup_distribution = taxi_analyzer.get_pickup_distribution()

            rate_summary = taxi_analyzer.get_rate_stats()
            distance_summary = taxi_analyzer.get_distance_stats()


        except LookupError:
            print "Error"
            results_flag = False
            error_message = 'There is no data for this day or this location. Please try another another combination'

    context = RequestContext(request, {
        'original_date': original_date,
        'drop_offs': drop_offs,
        'current_lat': Decimal(current_lat),
        'current_long': Decimal(current_long),
        'results_flag': results_flag,
        'number_dropoffs': number_dropoffs,
        'cluster_list': cluster_list,
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
    clusters = None

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

        clusters, cluster_list = get_cluster_listthing(dropoffs_df)
        #print clusters
        #print "======="
        #print cluster_list

    context = RequestContext(request, {
        'drop_offs': drop_offs,
        'current_lat': Decimal(current_lat),
        'current_long': Decimal(current_long),
        'results_flag': results_flag,
        'number_dropoffs': number_dropoffs,
        'clusters': clusters,
        'cluster_list': cluster_list,
    })
    return render(request, 'taxis/coordinates_test.html', context)