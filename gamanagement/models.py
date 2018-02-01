from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.urls import reverse
import datetime

AYEAR_CHOICES = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'))
SEASON_CHOICES = (('W', 'Winter'), ('A', 'Autumn'))

class Attribute(models.Model):
    ID = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True)
    current_flag = models.BooleanField(default=True)
    def __str__(self):
        return self.attributeID + ' ' + self.name

class Indicator(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT)
    course = models.ManyToManyField('Course', through='Indicator_Course')
    ID = models.CharField(max_length=20)
    description = models.CharField(max_length=1000)
    current_flag = models.BooleanField(default=True)
    def __str__(self):
        return self.indicatorID

class Indicator_Course(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    introduced = models.BooleanField(default=False)
    taught = models.BooleanField(default=False)
    used = models.BooleanField(default=False)
    assessmentMethod = models.OneToOneField('AssessmentMethod', 
                                            on_delete=models.PROTECT,
                                            null=True)
    
class AssessmentMethod(models.Model):
    criteria = models.CharField(max_length=1000)
    expectation4 = models.CharField(max_length=1000)
    expectation3 = models.CharField(max_length=1000)
    expectation2 = models.CharField(max_length=1000)
    expectation1 = models.CharField(max_length=1000)
    time_year = models.CharField(max_length=1, 
                                 choices=AYEAR_CHOICES)
    time_semester = models.CharField(max_length=1, 
                                     choices=SEASON_CHOICES)

class Department(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Profile(models.Model):
    course = models.ManyToManyField('Course')
    department = models.ManyToManyField('Department')
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Course(models.Model):
    ID = models.CharField(max_length=20, primary_key=True)
    department = models.ManyToManyField(Department)
    current_flag = models.BooleanField(default=True)
    def __str__(self):
        return self.courseID

class Assessment(models.Model):
    indicator_course = models.ForeignKey(Indicator_Course, 
                                         on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    numOf4 = models.PositiveSmallIntegerField(blank=True, null=True)
    numOf3 = models.PositiveSmallIntegerField(blank=True, null=True)
    numOf2 = models.PositiveSmallIntegerField(blank=True, null=True)
    numOf1 = models.PositiveSmallIntegerField(blank=True, null=True)
    semester = models.OneToOneField('SemesterLU', on_delete=models.PROTECT)
    def get_absolute_url(self):
        return reverse('assessments-view')
        
class SemesterLU(models.Model):
    year = models.CharField(max_length=4, default=datetime.datetime.now().year)
    semester = models.CharField(max_length=1, choices=SEASON_CHOICES)


