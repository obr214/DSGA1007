# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TaxiPickUps',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vendor_id', models.IntegerField(null=True, verbose_name=b'Vendor Id', blank=True)),
                ('pickup_datetime', models.DateTimeField(null=True, verbose_name=b'Pick Up Datetime', blank=True)),
                ('dropoff_datetime', models.DateTimeField(null=True, verbose_name=b'Drop Off Datetime', blank=True)),
                ('passenger_count', models.IntegerField(null=True, verbose_name=b'Passenger Count', blank=True)),
                ('trip_distance', models.FloatField(null=True, verbose_name=b'Trip Distance', blank=True)),
                ('pickup_longitude', models.DecimalField(null=True, verbose_name=b'Pick Up Longitude', max_digits=17, decimal_places=14, blank=True)),
                ('pickup_latitude', models.DecimalField(null=True, verbose_name=b'Pick Up Latitude', max_digits=17, decimal_places=14, blank=True)),
                ('rate_code_id', models.IntegerField(null=True, verbose_name=b'Rate Code', blank=True)),
                ('store_and_fwd_flag', models.CharField(max_length=2, null=True, verbose_name=b'Store n F Flag', blank=True)),
                ('dropoff_longitude', models.DecimalField(null=True, verbose_name=b'Drop Off Longitude', max_digits=17, decimal_places=14, blank=True)),
                ('dropoff_latitude', models.DecimalField(null=True, verbose_name=b'Drop Off Longitude', max_digits=17, decimal_places=14, blank=True)),
                ('payment_type', models.IntegerField(null=True, verbose_name=b'Payment Type', blank=True)),
                ('fare_amount', models.FloatField(null=True, verbose_name=b'Fare Amount', blank=True)),
                ('extra', models.FloatField(null=True, verbose_name=b'Extra Amount', blank=True)),
                ('mta_tax', models.FloatField(null=True, verbose_name=b'MTA Tax', blank=True)),
                ('tip_amount', models.FloatField(null=True, verbose_name=b'Tip Amount', blank=True)),
                ('tolls_amount', models.FloatField(null=True, verbose_name=b'Tolls Amount', blank=True)),
                ('total_amount', models.FloatField(null=True, verbose_name=b'Total Amount', blank=True)),
            ],
        ),
    ]
