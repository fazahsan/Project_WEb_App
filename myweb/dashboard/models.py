from django.db import models

from django.db import models

class DataPoint(models.Model):
    name = models.CharField(max_length=100)
    value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return self.name

