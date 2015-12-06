import numpy as np
from decimal import Decimal
from django.db import connection
from sklearn.cluster import DBSCAN
#from math import sin, cos, sqrt, atan2, radians


def format_date(datetime_string):
    try:
        pickup_date_arr = datetime_string.split('/')
        pickup_date = pickup_date_arr[2]+'-'+pickup_date_arr[0]+'-'+pickup_date_arr[1]
        #pickup_date = '2015-01-01'
        pickup_date_init = pickup_date + ' 00:00:00'
        pickup_date_end = pickup_date + ' 23:59:59'
        return pickup_date_init, pickup_date_end
    except LookupError:
        return None, None


def dictfetchall(cursor):
    #Return all rows from a cursor as a dict
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


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

"""
def get_distance_coordinates(latitude_1, longitude_1, latitude_2, longitude_2):
    r = 6373.0

    lat1 = radians(latitude_1)
    lon1 = radians(longitude_1)
    lat2 = radians(latitude_2)
    lon2 = radians(longitude_2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = r * c

    return distance
"""

def get_central_coordinate(latitude_list, longitude_list):
    if len(latitude_list) == len(longitude_list):

        number_of_coordinates = len(longitude_list)
        #If the dataframe contains just one row, it returns that point.
        if len(latitude_list.index) == 1:
            #Returns a tuple
            return latitude_list.iat[0,0], longitude_list.iat[0,0]
        else:
            x_value = 0
            y_value = 0
            z_value = 0

            #Creates Numpy Arrays
            lats = np.asarray(latitude_list)
            longitude = np.asarray(longitude_list)

            lats = lats * float(np.pi)/float(180)
            longitude = longitude * float(np.pi)/float(180)
            print lats
            lat_cosine = np.cos(lats)
            print "After cos"
            long_cosine = np.cos(longitude)
            long_sin = np.sin(longitude)
            lat_sin = np.sin(lats)

            x = np.sum(lat_cosine*long_cosine)
            y = np.sum(lat_cosine*long_sin)
            z = np.sum(lat_sin)

            x = x/float(number_of_coordinates)
            y = y/float(number_of_coordinates)
            z = z/float(number_of_coordinates)

            centralLongitude = np.arctan2(y, x)
            centralSquareRoot = np.sqrt(x * x + y * y)
            centralLatitude = np.arctan2(z, centralSquareRoot)

            return centralLatitude * 180 / np.pi, centralLongitude * 180 / np.pi

    else:
        return None, None


def get_cluster_list(dataframe):
    coordinates = dataframe.as_matrix(columns=['dropoff_longitude', 'dropoff_latitude'])

    db_scan = DBSCAN(eps=.01, min_samples=1).fit(coordinates)
    labels = db_scan.labels_

    labels_set = set(labels)
    num_clusters = len(set(labels))

    dataframe['cluster'] = labels

    dataframe['cluster_center_lat'] = np.nan
    dataframe['cluster_center_long'] = np.nan

    for label in labels_set:
        #Filter the rows per cluster
        cluster_df = dataframe.loc[dataframe['cluster'] == label]

        lat_list = cluster_df['dropoff_latitude']
        long_list = cluster_df['dropoff_longitude']

        #Gets the center of that set of coordinates
        lat_cent, long_cent = get_central_coordinate(lat_list, long_list)

        #Saves the centered lat/long in their respective colum
        dataframe.cluster_center_lat[dataframe.cluster==label] = lat_cent
        dataframe.cluster_center_long[dataframe.cluster==label] = long_cent

    #dataframe['distance_center'] = dataframe.apply(get_distance_coordinates, axis=1)

    #max_distances = dataframe.groupby(['cluster'], sort=False)['distance_center'].max()
    cluster_rows = dataframe.groupby(['cluster'], sort=False).first()

    cluster_df = cluster_rows[['cluster_center_lat', 'cluster_center_long']]
    #cluster_df['max_distances'] = max_distances

    return cluster_df.values.tolist()