from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.urls import reverse
from django.db.models.signals import m2m_changed, pre_save
from django.core import exceptions
import datetime


AYEAR_CHOICES = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'))
SEASON_CHOICES = (('W', 'Winter'), ('A', 'Autumn'))


class Attribute(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True)
    current_flag = models.BooleanField(default=True)
    
    def __str__(self):
        return self.code + ' ' + self.name


class Indicator(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT)
    code = models.CharField(max_length=20)
    programs = models.ManyToManyField('Program')
    description = models.TextField(max_length=1000)
    introduced = models.ManyToManyField('Course', related_name='introduces', blank=True)
    taught = models.ManyToManyField('Course', related_name='taught', blank=True)
    used = models.ManyToManyField('Course', related_name='used', blank=True)
    assessed = models.ManyToManyField('Course', through='AssessmentMethod', blank=True)
    current_flag = models.BooleanField(default=True)
    
    def __str__(self):
        return self.code
  
    
class AssessmentMethod(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.PROTECT)
    course = models.ForeignKey('course', on_delete=models.PROTECT)
    criteria = models.CharField(max_length=1000)
    expectation4 = models.TextField(max_length=1000)
    expectation3 = models.TextField(max_length=1000)
    expectation2 = models.TextField(max_length=1000)
    expectation1 = models.TextField(max_length=1000)
    time_year = models.CharField(max_length=1, 
                                 choices=AYEAR_CHOICES)
    time_semester = models.CharField(max_length=1, 
                                     choices=SEASON_CHOICES)

class Program(models.Model):
    name = models.CharField(max_length=50)
    current_flag = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        try:
            prog = Program.objects.get(name=self.name)
            prog.current_flag=True
            super(Program, prog).save(*args, **kwargs)
        except Program.DoesNotExist:
            super().save(*args, **kwargs)
            

class Course(models.Model):
    code = models.CharField(max_length=20)
    teachers = models.ManyToManyField(User, blank=True)
    
    def __str__(self):
        return self.code
                

class Assessment(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
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
  
    class Meta:
        unique_together = (('semester','teacher','assessmentMethod','program'),)
        
        
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
                for program in am.indicator.programs.all():
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


def indicatorProgramChange(sender, **kwargs):
    pk_set = kwargs['pk_set']
    ind = kwargs['instance']
    currentSemester = SemesterLU.objects.latest()
    ams = ind.assessmentmethod_set.all()
    teachers = set([
        t for l in [am.course.teachers.all() for am in ams] for t in l
    ])
    
    if kwargs['action'] == 'post_add':
        programs = [Program.objects.get(pk = pk) for pk in pk_set]
        for teacher in teachers:
            print(teacher)
            for program in programs:
                for am in ams:
                    print(program)
                    print(am)
                    print(teacher)
                    print(currentSemester)
                    Assessment.objects.get_or_create(
                        program = program,
                        assessmentMethod = am,
                        teacher = teacher,
                        semester = currentSemester
                    )
        
    if kwargs['action'] == 'pre_remove':
        programs = [Program.objects.get(pk=pk) for pk in pk_set]
        for program in programs:
            for am in ams:
                assessments = Assessment.objects.all().filter(
                    assessmentMethod = am,
                    semester = currentSemester,
                    program = program
                )
                for assessment in assessments:
                    assessment.delete()
        
    
m2m_changed.connect(courseTeacherChange, sender=Course.teachers.through)
m2m_changed.connect(indicatorProgramChange, sender=Indicator.programs.through)
 
