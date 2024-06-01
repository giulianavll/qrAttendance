from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    # id = models.IntegerField(primary_key=True, unique=True)
    key = models.CharField(max_length=16, unique=True)  # dni/ce
    name = models.CharField(max_length=128)
    group = models.CharField(max_length=16)
    code = models.CharField(max_length=64)


#     class Meta:
#         ordering = ["key"]


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
