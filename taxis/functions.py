import numpy as np

"""
File that contains general functions.
"""


def format_date(datetime_string):
    """
    Function that formats a date in a specific format

    :param datetime_string with the format 12/01/2015
    :return: Two string dates with the format year-month-day HH:MM:SS
    """
    try:
        pickup_date_arr = datetime_string.split('/')
        pickup_date = pickup_date_arr[2] + '-' + pickup_date_arr[0] + '-' + pickup_date_arr[1]
        pickup_date_init = pickup_date + ' 00:00:00'
        pickup_date_end = pickup_date + ' 23:59:59'
        return pickup_date_init, pickup_date_end
    except LookupError:
        return None, None


def dictfetchall(cursor):
    """
    Function that transform a queryset to a dictionary in order to be manipulated in an easier way.

    :param cursor: A queryset
    :return: A dictionary with the data from the queryset
    """
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
        ]


def get_centroid(points):
    """
    Function that obtains the centroid of a list of latitudes and longitudes

    :param points: A list of coordinates (Lat and Long)
    :return: A list with two elements, a longitude and a latitude
    """
    total_points = points.shape[0]
    sum_lon = np.sum(points[:, 1])
    sum_lat = np.sum(points[:, 0])
    return [sum_lon/total_points, sum_lat/total_points]


def get_distances(coordinates_list, latitude_ref, longitude_ref):
    """
    Functions that calculates the distances between a list of coordinates and a references point

    :param coordinates_list: A list of latitudes and longitudes
    :param latitude_ref: The latitude reference point
    :param longitude_ref: The longitude reference point
    :return: A list with the distances between each coordinate and the reference point
    """
    distances = []
    for coord in coordinates_list:
        distances.append(get_distance_coordinates(coord[1], coord[0], latitude_ref, longitude_ref))
    return distances
