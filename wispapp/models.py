from django.db import models
from django.contrib.auth.models import User

class Household(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='households')

    def __str__(self):
        return self.name

class Member(models.Model):
    name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Distribution_type(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    distribution_type = models.ForeignKey(Distribution_type, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f'{self.name} ({self.distribution_type})'

class Period(models.Model):
    period = models.CharField(max_length=100)

    def __str__(self):
        return self.period

class Movement(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    period = models.ForeignKey(Period, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return f'{self.member} - {self.amount}'

class Salary(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.ForeignKey(Period, on_delete=models.CASCADE, default=0)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)

    def __str__(self):
        return f'Salary for {self.member} during {self.period}'
