from django.db import models

# Create your models here.
class Census(models.Model):
    SUMLEV = models.IntegerField()
    STATE = models.IntegerField()
    COUNTY = models.IntegerField()
    PLACE = models.IntegerField()
    COUSUB = models.IntegerField()
    CONCIT = models.IntegerField()
    PRIMGEO_FLAG = models.IntegerField
    FUNCSTAT = models.CharField(max_length=100)
    NAME = models.CharField(max_length=100)
    STNAME = models.CharField(max_length=100)
    CENSUS2010POP = models.IntegerField()
    ESTIMATESBASE2010 = models.IntegerField()
    POPESTIMATE2010 = models.IntegerField()
    POPESTIMATE2011 = models.IntegerField()
    POPESTIMATE2012 = models.IntegerField()
    POPESTIMATE2013 = models.IntegerField()
    POPESTIMATE2014 = models.IntegerField()
    POPESTIMATE2015 = models.IntegerField()
    POPESTIMATE2016 = models.IntegerField()
    POPESTIMATE2017 = models.IntegerField()
    POPESTIMATE2018 = models.IntegerField()
    POPESTIMATE2019 = models.IntegerField()
