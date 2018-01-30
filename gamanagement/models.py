from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.urls import reverse

class Attribute(models.Model):
    attributeID = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.attributeID + ' ' + self.name

class Indicator(models.Model):
    indicatorID = models.CharField(max_length=20)
    description = models.CharField(max_length=1000)
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT)
    utilizedIn = models.ManyToManyField('Course', through='Utilized', related_name='utilizedIn')
    introducedIn = models.ManyToManyField('Course', through='Introduced', related_name='introducedIn')
    taughtIn = models.ManyToManyField('Course', through='Taught', related_name='taughtIn')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.indicatorID

class AssessmentMethod(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.PROTECT)
    expectation4 = models.CharField(max_length=1000)
    expectation3 = models.CharField(max_length=1000)
    expectation2 = models.CharField(max_length=1000)
    expectation1 = models.CharField(max_length=1000)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)

class Department(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.name

class Profile(models.Model):
    course = models.ManyToManyField('Course')
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)

class Course(models.Model):
    courseID = models.CharField(max_length=20)
    assessmentMethod = models.ManyToManyField(AssessmentMethod)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.courseID
    
class Utilized(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    current_flag = models.BooleanField()

class Introduced(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    current_flag = models.BooleanField()

class Taught(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    current_flag = models.BooleanField()

class Assessment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    assessmentMethod = models.ForeignKey(AssessmentMethod, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    description = models.CharField(max_length=1000)
    numOf4 = models.PositiveSmallIntegerField(blank=True, null=True)
    numOf3 = models.PositiveSmallIntegerField(blank=True, null=True)
    numOf2 = models.PositiveSmallIntegerField(blank=True, null=True)
    numOf1 = models.PositiveSmallIntegerField(blank=True, null=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    
    def get_absolute_url(self):
        return reverse('assessments-view')


