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
    description = models.TextField(max_length=1000)
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
    programs = models.ManyToManyField('Program')
    criteria = models.CharField(max_length=1000)
    expectation4 = models.TextField(max_length=1000)
    expectation3 = models.TextField(max_length=1000)
    expectation2 = models.TextField(max_length=1000)
    expectation1 = models.TextField(max_length=1000)
    time_year = models.CharField(max_length=1, 
                                 choices=AYEAR_CHOICES)
    time_semester = models.CharField(max_length=1, 
                                     choices=SEASON_CHOICES)
    current_flag = models.BooleanField(default=True)


class Program(models.Model):
    name = models.CharField(max_length=50)
    current_flag= models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
        
    def delete(self):
        if self.assessment_set.all().count() == 0:
            super(Program, self).delete()
        else:
            assessments = self.assessment_set.all().filter(semester=SemesterLU.objects.latest())
            for assessment in assessments:
                assessment.delete()
            self.current_flag = False
            self.save()


class Course(models.Model):
    ID = models.CharField(max_length=20, primary_key=True)
    teachers = models.ManyToManyField(User, blank=True)
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
    
    def __str__(self):
        return str(self.pk)
        
        
class SemesterLU(models.Model):
    year = models.CharField(max_length=4, default=datetime.datetime.now().year)
    term = models.CharField(max_length=1, choices=SEASON_CHOICES)
    class Meta:
        get_latest_by = ['year', '-term']
        unique_together = (('year', 'term'),)
    

def courseTeacherChange(sender, **kwargs):
    pk_set = kwargs['pk_set']
    course = kwargs['instance']
    currentSemester = SemesterLU.objects.latest()
    print(currentSemester)
    if kwargs['action'] == 'post_add' :
        for pk in pk_set:
            teacher = User.objects.get(pk=pk)
            for am in course.assessmentmethod_set.all():
                for program in am.programs.all():
                    Assessment.objects.get_or_create(
                        program=program,
                        assessmentMethod=am,
                        teacher=teacher,
                        semester=currentSemester
                    )
                    
    
    elif kwargs['action'] == 'pre_remove' :
        for pk in pk_set:
            teacher = User.objects.get(pk=pk)
            for am in course.assessmentmethod_set.all():
                assessments = Assessment.objects.all().filter(
                    teacher = teacher,
                    assessmentMethod = am,
                    semester = currentSemester
                )
                for assessment in assessments:
                    assessment.delete()


def assessmentMethodProgramChange(sender, **kwargs):
    pk_set = kwargs['pk_set']
    am = kwargs['instance']
    currentSemester = SemesterLU.objects.latest() 
    print(currentSemester)
    teachers = am.course.teachers.all()
    
    if kwargs['action'] == 'post_add':
        programs = [Program.objects.get(pk = pk) for pk in pk_set]

        for teacher in teachers:
            for program in programs:
                Assessment.objects.get_or_create(
                    program = program,
                    assessmentMethod = am,
                    teacher = teacher,
                    semester = currentSemester
                )
    
    if kwargs['action'] == 'pre_remove':
        programs = [Program.objects.get(pk=pk) for pk in pk_set]
        for program in programs:
            assessments = Assessment.objects.all().filter(
                assessmentMethod = am,
                semester = currentSemester,
                program = program
            )
            for assessment in assessments:
                assessment.delete()
        
    
m2m_changed.connect(courseTeacherChange, sender=Course.teachers.through)
m2m_changed.connect(assessmentMethodProgramChange, sender=AssessmentMethod.programs.through)
 
