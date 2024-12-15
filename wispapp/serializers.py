from rest_framework import serializers
from .models import Movement, Member, Category, Distribution_type, Salary, Period

class MovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movement
        fields = ['id', 'amount', 'date', 'member', 'category']

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'name']

class DistributionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distribution_type
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'distribution_type']

class SalarySerializer(serializers.ModelSerializer):
    
    class Meta: 
        model = Salary
        fields = ['id', 'date', 'amount', 'member']

class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ['id', 'period']