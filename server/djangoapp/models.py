import json
from django.db import models
from django.utils.timezone import now


class CarMake(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(null=False, max_length=30)
    description = models.CharField(null=False, max_length=250)

    def __str__(self):
        return self.name


class CarModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    make = models.ForeignKey(CarMake, null=False, on_delete=models.CASCADE)
    dealer_id = models.IntegerField()
    name = models.CharField(null=False, max_length=30)
    TYPE_CHOICES = [
        ('SEDAN', 'Sedan'),
        ('SUV', 'SUV'),
        ('WAGON', 'Wagon'),
        ('HATCHBACK', 'Hatchback'),
        ('COUPE', 'Coupe'),
        ('CONVERTIBLE', 'Convertible'),
        ('MINIVAN', 'Minivan')
    ]
    type = models.CharField(
        null=False,
        max_length=20,
        choices=TYPE_CHOICES,
        default='SEDAN'
    )
    colour = models.CharField(null=False, max_length=30)
    year = models.DateField(null=False)

    def __str__(self):
        return self.name


class CarDealer:

    def __init__(self, address, city, full_name, id, lat, long, short_name, st, state, zip):
        self.address = address
        self.city = city
        self.full_name = full_name
        self.id = id
        self.lat = lat
        self.long = long
        self.short_name = short_name
        self.st = st
        self.state = state
        self.zip = zip

    def __str__(self):
        return json.dumps(self.__dict__, indent=2)


class DealerReview:

    def __init__(self, car_make, car_model, car_year, dealership, id, name, purchase, purchase_date, review, sentiment):
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.dealership = dealership
        self.id = id
        self.name = name
        self.purchase = purchase
        self.purchase_date = purchase_date
        self.review = review
        self.sentiment = sentiment

    def __str__(self):
        return json.dumps(self.__dict__, indent=2)
