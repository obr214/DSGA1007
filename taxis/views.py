from decimal import Decimal
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse
from django.utils.encoding import smart_str
from DSGA1007 import settings
from taxi_analyzer import TaxiAnalyzer


def pick_ups(request):
    """
    Main Pick Up functions.
    It generates all the analysis for the pick ups.
    """
    
    #Initializes the variables
    original_date = ''
    error_message = None
    drop_offs = None
    results_flag = False
    number_dropoffs = None
    cluster_list = None
    pickup_distribution = None
    rate_summary = None
    distance_summary = None

    #Set the initial pair of coordinates
    current_lat = '40.730610'
    current_long = '-73.935242'

    if request.method == 'POST':
        results_flag = True

        #Gets the Latitude, the Longitude and the Date from the HTML
        current_lat = request.POST.get('pick_up_lat', '40.730610')
        current_long = request.POST.get('pick_up_lon',  '-73.935242')
        pickup_date = request.POST.get('pickup_date', '01/01/2015')
        original_date = pickup_date

        try:
            taxi_analyzer = TaxiAnalyzer()
            taxi_analyzer.get_data(pickup_date, current_long, current_lat)
            drop_offs = taxi_analyzer.get_dropoffs()
            number_dropoffs = taxi_analyzer.get_size()

            #Get the Clusters
            cluster_list = taxi_analyzer.get_top_clusters(20)

            #Gets the Pick Up distribution through the day
            pickup_distribution = taxi_analyzer.get_pickup_distribution()

            #Get the summary statistics
            rate_summary = taxi_analyzer.get_rate_stats()
            distance_summary = taxi_analyzer.get_distance_stats()

            #Creates the Report File
            taxi_analyzer.create_report()

        except LookupError as lookup_error_message:
            results_flag = False
            error_message = lookup_error_message
        except IOError as io_error_message:
            results_flag = False
            error_message = io_error_message

    #Send all the variables back to the HTML for displaying
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
    return render(request, 'taxis/pick_ups.html', context)


def get_report_file(request):
    if request.method == 'POST':
        url_file = settings.MEDIA_ROOT
        file_name = 'yellow_cap_analysis.pdf'
        print "Im here"
        response = HttpResponse(mimetype='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
        response['X-Sendfile'] = smart_str(url_file)
        print response

        return response
