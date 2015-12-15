
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from DSGA1007 import settings
from taxi_analyzer_exception import TaxiAnalyzerException
from functions import dictfetchall, format_date, get_centroid, get_distances
from collections import OrderedDict
from django.db import connection
from sklearn.cluster import DBSCAN
from matplotlib.backends.backend_pdf import PdfPages


class TaxiAnalyzer:

    def __init__(self):
        self.taxi_dataframe = None

    def get_data(self, date, longitud, latitude):

        date_init, date_end = format_date(date)

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
                       [latitude, longitud, latitude, date_init, date_end]
                       )
        try:
            self.taxi_dataframe = pd.DataFrame(dictfetchall(cursor))
            self.taxi_dataframe['pickup_datetime'] = pd.to_datetime(self.taxi_dataframe['pickup_datetime'])
        except KeyError:
            raise KeyError("No data for this date or this location. Please select another one")

    def get_size(self):
        return len(self.taxi_dataframe.index)

    def get_dropoffs(self):
        dropoffs = self.taxi_dataframe[['dropoff_latitude', 'dropoff_longitude']]
        return dropoffs.values.tolist()

    def get_top_clusters(self, number_clusters):
        try:
            coordinates = self.taxi_dataframe.as_matrix(columns=['dropoff_longitude', 'dropoff_latitude'])

            clusters = None
            number_of_rows = len(self.taxi_dataframe.index)
            cluster_stop_flag = True
            #Starting EPS
            current_eps = .005

            while cluster_stop_flag:
                db_scan = DBSCAN(eps=current_eps, min_samples=1).fit(coordinates)
                labels = db_scan.labels_

                num_clusters = len(set(labels))

                clusters = pd.Series([coordinates[labels == i] for i in xrange(num_clusters)])
                sorted_len_clusters = sorted(clusters.values.tolist(), key=len, reverse=True)

                current_eps -= .0005
                if len(sorted_len_clusters[0]) <= int(number_of_rows*0.15):
                    cluster_stop_flag = False

                    top_ten_clusters = sorted_len_clusters[:number_clusters]

                    clusters = pd.Series(top_ten_clusters)

            clusters_centroids = []
            for i, cluster in clusters.iteritems():

                list_center = get_centroid(cluster)

                distances = get_distances(cluster, list_center[0], list_center[1])

                max_distance = np.amax(distances)
                list_center.append(max_distance)
                clusters_centroids.append(list_center)

            return clusters_centroids

        except LookupError:
            raise LookupError("Columns dropoff_longitude/dropoff_latitude not found")

    def get_pickup_distribution(self):
        pickup_distribution = OrderedDict()
        hour_range = pd.date_range('00:00:00', periods=24, freq='H')

        for hour in hour_range:
            hour_string = hour.strftime("%H:%M")
            pickup_distribution[hour_string] = 0

        times = pd.DatetimeIndex(self.taxi_dataframe.pickup_datetime)

        hour_groups = self.taxi_dataframe.groupby([times.hour]).size()
        for hg in hour_groups.index:
            #Leading zeros
            hour_string = str(hg).zfill(2)+':00'
            pickup_distribution[hour_string] = int(hour_groups[hg])

        return pickup_distribution

    def get_rate_stats(self):
        rate_summary = OrderedDict()

        rate_sum_statistics = self.taxi_dataframe['total_amount'].describe()
        rate_summary['Mean'] = rate_sum_statistics['mean']
        rate_summary['Std Dev'] = rate_sum_statistics['std']
        rate_summary['25%'] = rate_sum_statistics['25%']
        rate_summary['50%'] = rate_sum_statistics['50%']
        rate_summary['75%'] = rate_sum_statistics['75%']
        rate_summary['Max'] = rate_sum_statistics['max']

        return rate_summary

    def get_distance_stats(self):
        distance_summary = OrderedDict()
        distance_sum_statistics = self.taxi_dataframe['trip_distance'].describe()
        distance_summary['Mean'] = distance_sum_statistics['mean']
        distance_summary['Std Dev'] = distance_sum_statistics['std']
        distance_summary['25%'] = distance_sum_statistics['25%']
        distance_summary['50%'] = distance_sum_statistics['50%']
        distance_summary['75%'] = distance_sum_statistics['75%']
        distance_summary['Max'] = distance_sum_statistics['max']

        return distance_summary

    def get_amount_info(self):
        pass

    def create_report(self):
        url_file = settings.MEDIA_ROOT
        file_name = 'yellow_cap_analysis.pdf'
        print "Inside Create"
        print url_file

        with PdfPages(url_file+file_name) as pdf:

            #Get the pick up distribution
            pickup_dist = self.get_pickup_distribution()
            x = np.arange(len(pickup_dist))
            plt.bar(x, pickup_dist.values(), align="center")
            plt.xticks(x, pickup_dist.keys(), rotation='vertical')
            plt.title("Pick Ups Distribution Over Time")
            plt.xlabel("Time of the Day")
            plt.ylabel("Number of Pick Ups")
            pdf.savefig()
            plt.close()

            x = np.arange(0, 5, 0.1)
            y = np.sin(x)
            plt.plot(x, y)
            pdf.savefig()
            plt.close()


