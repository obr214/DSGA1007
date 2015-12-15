import numpy as np
import pandas as pd
from django.db import connection
from sklearn.cluster import DBSCAN


def format_date(datetime_string):
    try:
        pickup_date_arr = datetime_string.split('/')
        pickup_date = pickup_date_arr[2] + '-' + pickup_date_arr[0] + '-' + pickup_date_arr[1]
        # pickup_date = '2015-01-01'
        pickup_date_init = pickup_date + ' 00:00:00'
        pickup_date_end = pickup_date + ' 23:59:59'
        return pickup_date_init, pickup_date_end
    except LookupError:
        return None, None


def dictfetchall(cursor):
    # Return all rows from a cursor as a dict
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
        ]


def get_centroid(points):
    total_points = points.shape[0]
    sum_lon = np.sum(points[:, 1])
    sum_lat = np.sum(points[:, 0])
    return [sum_lon/total_points, sum_lat/total_points]


def get_distances(coordinates_list, latitude_ref, longitude_ref):
    distances = []
    for coord in coordinates_list:
        distances.append(get_distance_coordinates(coord[1], coord[0], latitude_ref, longitude_ref))
    return distances


#==================================================================


def get_dropoffs_df_from_db(current_lat, current_long, pickup_date_init, pickup_date_end):
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
    return drop_offs



def get_distance_coordinates(latitude_1, longitude_1, latitude_2, longitude_2):
    r = 6373000.0

    lat1 = np.radians(latitude_1)
    lon1 = np.radians(longitude_1)
    lat2 = np.radians(latitude_2)
    lon2 = np.radians(longitude_2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    distance = r * c

    return distance


def get_distances(coordinates_list, latitude_ref, longitude_ref):
    distances = []
    for coord in coordinates_list:
        distances.append(get_distance_coordinates(coord[1], coord[0], latitude_ref, longitude_ref))
    return distances


def get_distance_coordinates__(x):
    "Returns the distance in km"

    latitude_1 = x['dropoff_latitude']
    longitude_1 = x['dropoff_longitude']
    latitude_2 = x['cluster_center_lat']
    longitude_2 = x['cluster_center_long']

    r = 6373.0

    lat1 = np.radians(latitude_1)
    lon1 = np.radians(longitude_1)
    lat2 = np.radians(latitude_2)
    lon2 = np.radians(longitude_2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    distance = r * c

    return distance*1000


def getCentroid(points):
    total_points = points.shape[0]
    sum_lon = np.sum(points[:, 1])
    sum_lat = np.sum(points[:, 0])
    return [sum_lon/total_points, sum_lat/total_points]

def get_central_coordinate(latitude_list, longitude_list):
    if len(latitude_list) == len(longitude_list):

        number_of_coordinates = len(longitude_list)
        # If the dataframe contains just one row, it returns that point.
        if len(latitude_list.index) == 1:
            # Returns a tuple
            return latitude_list.iat[0, 0], longitude_list.iat[0, 0]
        else:
            x_value = 0
            y_value = 0
            z_value = 0

            # Creates Numpy Arrays
            lats = np.asarray(latitude_list)
            longitude = np.asarray(longitude_list)

            lats = lats * float(np.pi) / float(180)
            longitude = longitude * float(np.pi) / float(180)
            lat_cosine = np.cos(lats)
            long_cosine = np.cos(longitude)
            long_sin = np.sin(longitude)
            lat_sin = np.sin(lats)

            x = np.sum(lat_cosine * long_cosine)
            y = np.sum(lat_cosine * long_sin)
            z = np.sum(lat_sin)

            x = x / float(number_of_coordinates)
            y = y / float(number_of_coordinates)
            z = z / float(number_of_coordinates)

            centralLongitude = np.arctan2(y, x)
            centralSquareRoot = np.sqrt(x * x + y * y)
            centralLatitude = np.arctan2(z, centralSquareRoot)

            return [centralLatitude * 180 / np.pi, centralLongitude * 180 / np.pi]

    else:
        return None, None


def get_cluster_list(dataframe):
    coordinates = dataframe.as_matrix(columns=['dropoff_longitude', 'dropoff_latitude'])

    db_scan = DBSCAN(eps=.005, min_samples=1).fit(coordinates)
    labels = db_scan.labels_

    labels_set = set(labels)
    num_clusters = len(set(labels))

    dataframe['cluster'] = labels

    dataframe['cluster_center_lat'] = np.nan
    dataframe['cluster_center_long'] = np.nan

    for label in labels_set:
        # Filter the rows per cluster
        cluster_df = dataframe.loc[dataframe['cluster'] == label]

        lat_list = cluster_df['dropoff_latitude']
        long_list = cluster_df['dropoff_longitude']

        # Gets the center of that set of coordinates
        lat_cent, long_cent = get_central_coordinate(lat_list, long_list)

        # Saves the centered lat/long in their respective colum
        dataframe.cluster_center_lat[dataframe.cluster == label] = lat_cent
        dataframe.cluster_center_long[dataframe.cluster == label] = long_cent

    dataframe['distance_center'] = dataframe.apply(get_distance_coordinates, axis=1)

    max_distances = dataframe.groupby(['cluster'], sort=False)['distance_center'].max()
    cluster_rows = dataframe.groupby(['cluster'], sort=False).first()

    cluster_df = cluster_rows[['cluster_center_lat', 'cluster_center_long']]
    cluster_df['max_distances'] = max_distances

    return cluster_df.values.tolist()


def get_cluster_listthing(dataframe):
    coordinates = dataframe.as_matrix(columns=['dropoff_longitude', 'dropoff_latitude'])

    clusters = None
    number_of_rows = len(dataframe.index)
    cluster_stop_flag = True
    #Starts with .005
    current_eps = .005

    while cluster_stop_flag:
        db_scan = DBSCAN(eps=current_eps, min_samples=1).fit(coordinates)
        labels = db_scan.labels_

        labels_set = set(labels)
        num_clusters = len(set(labels))
        print "Num Clusters:", num_clusters

        clusters = pd.Series([coordinates[labels == i] for i in xrange(num_clusters)])

        sorted_len_clusters = sorted(clusters.values.tolist(), key=len, reverse=True)
        #print "Ordered Paths"
        #print sorted_len_clusters
        #print "*****************************"
        print "Len 1st Cluster:", len(sorted_len_clusters[0])

        current_eps -= .0005
        if len(sorted_len_clusters[0]) <= int(number_of_rows*0.15):
            cluster_stop_flag = False

            top_ten_clusters = sorted_len_clusters[:20]

            clusters = pd.Series(top_ten_clusters)
            print len(clusters)

    clusters_list = []
    centers = []
    for i, cluster in clusters.iteritems():
        print "Len", len(cluster)
        clusters_list.append(cluster.tolist())

        list_center = getCentroid(cluster)

        distances = get_distances(cluster, list_center[0], list_center[1])

        #print "Distances: ", distances
        max_distance = np.amax(distances)
        #print "Max: ", max_distance
        list_center.append(max_distance)
        centers.append(list_center)

    return clusters.values.tolist(), centers
    #return clusters_list, centers

