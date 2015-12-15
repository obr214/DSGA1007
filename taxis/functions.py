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
        raise LookupError("Date has a wrong format")


def dictfetchall(cursor):
    """
    Function that transform a queryset to a dictionary in order to be manipulated in an easier way.

    :param cursor: A queryset
    :return: A dictionary with the data from the queryset
    """
    try:
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
            ]
    except LookupError:
        raise LookupError("Cannot convert QuerySet to Dictionary")


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


def get_distance_coordinates(latitude_1, longitude_1, latitude_2, longitude_2):
    """
    Obtains the distance between two points

    :param latitude_1: Point One Latitude
    :param longitude_1: Point One Longitude
    :param latitude_2: Point Two Latitude
    :param longitude_2: Point Two Longitude
    :return: A distance in meters
    """
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
