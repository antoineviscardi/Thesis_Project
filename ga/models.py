from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.urls import reverse
from django.db.models.signals import m2m_changed, pre_save
import datetime

AYEAR_CHOICES = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'))
SEASON_CHOICES = (('W', 'Winter'), ('A', 'Autumn'))

class Attribute(models.Model):
    ID = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True)
    current_flag = models.BooleanField(default=True)
    def __str__(self):
        return self.ID + ' ' + self.name

class Indicator(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT)
    ID = models.CharField(max_length=20, primary_key=True)
    description = models.CharField(max_length=1000)
    introduced = models.ManyToManyField('Course', related_name='introduces', blank=True)
    taught = models.ManyToManyField('Course', related_name='taught', blank=True)
    used = models.ManyToManyField('Course', related_name='used', blank=True)
    assessed = models.ManyToManyField('Course', through='AssessmentMethod', blank=True)
    current_flag = models.BooleanField(default=True)
    def __str__(self):
        return self.ID
    
class AssessmentMethod(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.PROTECT)
    course = models.ForeignKey('course', on_delete=models.PROTECT)
    criteria = models.CharField(max_length=1000)
    expectation4 = models.CharField(max_length=1000)
    expectation3 = models.CharField(max_length=1000)
    expectation2 = models.CharField(max_length=1000)
    expectation1 = models.CharField(max_length=1000)
    time_year = models.CharField(max_length=1, 
                                 choices=AYEAR_CHOICES)
    time_semester = models.CharField(max_length=1, 
                                     choices=SEASON_CHOICES)
    current_flag = models.BooleanField(default=True)

class Program(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Profile(models.Model):
    program = models.ManyToManyField('Program', blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

class Course(models.Model):
    ID = models.CharField(max_length=20, primary_key=True)
    programs = models.ManyToManyField(Program)
    teachers = models.ManyToManyField(Profile, blank=True)
    current_flag = models.BooleanField(default=True)
    
    def __str__(self):
        return self.ID

class Assessment(models.Model):
    program = models.ForeignKey(Program, on_delete=models.PROTECT)
    assessmentMethod = models.ForeignKey(AssessmentMethod, 
                                         on_delete=models.PROTECT)
    teacher = models.ForeignKey(User, on_delete=models.PROTECT)
    numOf4 = models.PositiveSmallIntegerField('4', blank=True, null=True)
    numOf3 = models.PositiveSmallIntegerField('3', blank=True, null=True)
    numOf2 = models.PositiveSmallIntegerField('2', blank=True, null=True)
    numOf1 = models.PositiveSmallIntegerField('1', blank=True, null=True)
    semester = models.ForeignKey('SemesterLU', on_delete=models.PROTECT)
    
        
class SemesterLU(models.Model):
    year = models.CharField(max_length=4, default=datetime.datetime.now().year)
    term = models.CharField(max_length=1, choices=SEASON_CHOICES)
    class Meta:
        get_latest_by = ['year', '-term']
        unique_together = (('year', 'term'),)
    
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def courseTeacherChange(sender, **kwargs):
    pk_set = kwargs['pk_set']
    course = kwargs['instance']
    currentSemester = SemesterLU.objects.latest()
    if kwargs['action'] == 'post_add' :
        for pk in pk_set:
            teacher = Profile.objects.get(pk=pk)
            for am in course.assessmentmethod_set.all():
                for program in course.programs.all():
                    Assessment.objects.get_or_create(
                        program=program,
                        assessmentMethod=am,
                        teacher=teacher.user,
                        semester=currentSemester
                    )
                    
    
    elif kwargs['action'] == 'pre_remove' :
        for pk in pk_set:
            teacher = Profile.objects.get(pk=pk)
            for am in course.assessmentmethod_set.all():
                assessments = Assessment.objects.all().filter(
                    teacher = teacher.user,
                    assessmentMethod = am,
                    semester = currentSemester
                )
                for assessment in assessments:
                    assessment.delete()


def courseDepartmentChange(sender, **kwargs):
    pk_set = kwargs['pk_set']
    course = kwargs['instance']
    currentSemester = SemesterLU.objects.latest() 
    teachers = course.teachers.all()
    ams = course.assessmentmethod_set.all()
    
    if kwargs['action'] == 'post_add':
        programs = [Department.objects.get(pk = pk) for pk in pk_set]

        for teacher in teachers:
            for am in ams:
                for program in programss:
                    Assessment.objects.get_or_create(
                        program = program,
                        assessmentMethod = am,
                        teacher = teacher.user,
                        semester = currentSemester
                    )
    
    if kwargs['action'] == 'pre_remove':
        depts = [Department.objects.get(pk=pk) for pk in pk_set]
        for am in ams:
            for dept in depts:
                assessments = Assessment.objects.all().filter(
                    assessmentMethod = am,
                    semester = currentSemester,
                    department = dept
                )
                for assessment in assessments:
                    assessment.delete()
            
    
m2m_changed.connect(courseTeacherChange, sender=Course.teachers.through)
m2m_changed.connect(courseDepartmentChange, sender=Course.programs.through)


    
