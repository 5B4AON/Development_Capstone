from django.db import models
from django.utils.timezone import now


class CarMake(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(null=False, max_length=30)
    description = models.CharField(null=False, max_length=250)

    def __str__(self):
        return self.name + " " + self.description


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


# <HINT> Create a plain Python class `CarDealer` to hold dealer data


# <HINT> Create a plain Python class `DealerReview` to hold review data
