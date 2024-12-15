from django.shortcuts import render

from rest_framework import viewsets
from .models import Movement, Member, Category, Distribution_type, Salary, Period
from .serializers import MovementSerializer, MemberSerializer, CategorySerializer, DistributionTypeSerializer, SalarySerializer, PeriodSerializer

class MovementViewSet(viewsets.ModelViewSet):
    queryset = Movement.objects.all()
    serializer_class = MovementSerializer

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class DistributionTypeViewSet(viewsets.ModelViewSet):
    queryset = Distribution_type.objects.all()
    serializer_class = DistributionTypeSerializer

class SalaryViewSet(viewsets.ModelViewSet):
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer

class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer