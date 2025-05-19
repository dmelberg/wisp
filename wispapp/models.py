from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

class Household(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='households')

    def __str__(self):
        return self.name

class Member(models.Model):
    name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    household = models.ForeignKey(Household, on_delete=models.SET_NULL, null=True, blank=True, related_name='member_household')

    def __str__(self):
        return self.name

    @property
    def total_owed(self):
        """Sum of all movement distributions where this member is responsible for a share"""
        return MovementDistribution.objects.filter(
            member=self
        ).aggregate(total=Sum('amount'))['total'] or 0

    @property
    def total_paid(self):
        """Sum of all movements where this member was the payer"""
        return Movement.objects.filter(
            member=self
        ).aggregate(total=Sum('amount'))['total'] or 0

    @property
    def balance(self):
        """Total paid minus total owed"""
        return self.total_paid - self.total_owed

class Distribution_type(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='categories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    distribution_type = models.ForeignKey(Distribution_type, on_delete=models.CASCADE, default=1)

    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ['name', 'household']

    def __str__(self):
        return f"{self.name} ({self.household.name})"

class Period(models.Model):
    period = models.CharField(max_length=100)

    def __str__(self):
        return self.period

class Movement(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='movements')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='movements')
    description = models.TextField(blank=True, null=True)
    period = models.ForeignKey(Period, on_delete=models.CASCADE, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.member.name} - ${self.amount} - {self.category.name}"

class Salary(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.ForeignKey(Period, on_delete=models.CASCADE, default=0)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)

    def __str__(self):
        return f'Salary for {self.member} during {self.period}'

class MovementDistribution(models.Model):
    movement = models.ForeignKey(Movement, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_payer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)