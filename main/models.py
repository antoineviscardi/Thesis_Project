from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Attribute(models.Model):
    ID = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    current_flag = models.BooleanField()

class Indicator(models.Model):
    ID = models.CharField(max_length=20, primary_key=True)
    attributeID = models.ForeignKey(Attribute, on_delete=models.PROTECT)
    utilizedIn = models.ManyToManyField('Course', through='Utilized', related_name='utilizedIn')
    introducedIn = models.ManyToManyField('Course', through='Introduced', related_name='introducedIn')
    taughtIn = models.ManyToManyField('Course', through='Taught', related_name='taughtIn')
    expectation4 = models.CharField(max_length=1000)
    expectation3 = models.CharField(max_length=1000)
    expectation2 = models.CharField(max_length=1000)
    expectation1 = models.CharField(max_length=1000)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    current_flag = models.BooleanField()

class AssessmentMethod(models.Model):
    indicatorID = models.ForeignKey(Indicator, on_delete=models.PROTECT)
    course = models.ManyToManyField('Course', through='Course_AssessmentMethod')
    expectation4 = models.CharField(max_length=1000)
    expectation3 = models.CharField(max_length=1000)
    expectation2 = models.CharField(max_length=1000)
    expectation1 = models.CharField(max_length=1000)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    current_flag = models.BooleanField()

class Department(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)

class Profile(models.Model):
    departmentID = models.ForeignKey(Department, on_delete=models.PROTECT)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)

class Course(models.Model):
    ID = models.CharField(max_length=20, primary_key=True)
    userID = models.ForeignKey(User, on_delete=models.PROTECT)
    departmentID = models.ForeignKey(Department, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    current_flag = models.BooleanField()

class Utilized(models.Model):
    indicatorID = models.ForeignKey(Indicator, on_delete=models.PROTECT)
    courseID = models.ForeignKey(Course, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    current_flag = models.BooleanField()

class Introduced(models.Model):
    indicatorID = models.ForeignKey(Indicator, on_delete=models.PROTECT)
    courseID = models.ForeignKey(Course, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    current_flag = models.BooleanField()

class Taught(models.Model):
    indicatorID = models.ForeignKey(Indicator, on_delete=models.PROTECT)
    courseID = models.ForeignKey(Course, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    current_flag = models.BooleanField()

class Course_AssessmentMethod(models.Model):
    courseID = models.ForeignKey(Course, on_delete=models.PROTECT)
    AssesessmentMethodID = models.ForeignKey(AssessmentMethod, on_delete=models.PROTECT)
    description = models.CharField(max_length=1000)
    numOf4 = models.PositiveSmallIntegerField()
    numOf3 = models.PositiveSmallIntegerField()
    numOf2 = models.PositiveSmallIntegerField()
    numOf1 = models.PositiveSmallIntegerField()
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    current_flag = models.BooleanField()

'''
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
'''


