from django.test import TestCase

import os
from DSGA1007 import settings
from functions import *
from taxis.taxi_analyzer import TaxiAnalyzer


class Test(TestCase):

    def test_format_date_bad_format(self):
        """
        Passing a wrong format should raise a LookUp Error
        """
        wrong_date = '2015-0-'
        with self.assertRaises(LookupError):
            format_date(wrong_date)

    def test_get_distance_coordinates(self):
        """
        Passing the test if the functions returns the expected distance
        """
        distance = get_distance_coordinates(40.6722259521, -73.9717636108, 40.7249221802, -73.9955749512)
        self.assertEquals(int(distance), 6195)

    def test_empty_dataframe_empty_dataframe(self):
        """
        Passing the test if a Key Error is raised. Indicating that the dataframe is empty.
        """
        taxi_analyzer = TaxiAnalyzer()
        with self.assertRaises(KeyError):
            taxi_analyzer.get_data('01/01/2015', 40.7314230110458, -73.99699718035896)

    def test_get_data_csv_io_error(self):
        """
        Passing the test if a IOError is raised when a non existant filename is passed as parameter.
        """
        taxi_analyzer = TaxiAnalyzer()
        with self.assertRaises(IOError):
            taxi_analyzer.get_data_csv('wrong_file.csv')

    def test_get_size_not_none(self):
        """
        Passing the test if the function get_size() returns a value
        """
        taxi_analyzer = TaxiAnalyzer()
        taxi_analyzer.get_data_csv('test_.csv')
        number_dropoffs = taxi_analyzer.get_size()
        self.assertEqual(number_dropoffs, 161)

    def test_create_pdf(self):
        """
        Passing the test if the file is created successfully
        """
        url_file = settings.MEDIA_ROOT
        try:
            os.remove(url_file+'yellow_cab_analysis.pdf')
        except OSError:
            pass

        taxi_analyzer = TaxiAnalyzer()
        taxi_analyzer.get_data_csv('test_.csv')
        taxi_analyzer.create_report()

        self.assertTrue(os.path.isfile(url_file+'yellow_cab_analysis.pdf'))
