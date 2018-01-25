from django import forms

class GradeForm(froms.Form):
    numOf4 = models.PositiveSmallIntegerField()
    numOf3 = models.PositiveSmallIntegerField()
    numOf2 = models.PositiveSmallIntegerField()
    numOf1 = models.PositiveSmallIntegerField()
