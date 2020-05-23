from django.db import models

# Create your models here.
class Census(models.Model):
    sumlev = models.IntegerField()
    state = models.IntegerField()
    county = models.IntegerField()
    place = models.IntegerField()
    consub = models.IntegerField()
    concit = models.IntegerField()
    primgeo_flag = models.IntegerField
    funcstat = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    stname = models.CharField(max_length=100)
    census2010pop = models.IntegerField()
    estimatebase2010 = models.IntegerField()
    popestimate2010 = models.IntegerField()
    popestimate2011 = models.IntegerField()
    popestimate2012 = models.IntegerField()
    popestimate2013 = models.IntegerField()
    popestimate2014 = models.IntegerField()
    popestimate2015 = models.IntegerField()
    popestimate2016 = models.IntegerField()
    popestimate2017 = models.IntegerField()
    popestimate2018 = models.IntegerField()
    popestimate2019 = models.IntegerField()
