from rest_framework import serializers
from .models import Movement, Member, Category, Distribution_type, Salary, Period, Household
from django.db.models import Sum
from datetime import datetime, timedelta
from django.contrib.auth.models import User

class HouseholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Household
        fields = ['id', 'name']

class MemberSerializer(serializers.ModelSerializer):
    household = HouseholdSerializer(read_only=True)

    class Meta:
        model = Member
        fields = ['id', 'name', 'household']

class DistributionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distribution_type
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'household', 'created_at', 'updated_at']
        read_only_fields = ['household', 'created_at', 'updated_at']

class SalarySerializer(serializers.ModelSerializer):
    class Meta: 
        model = Salary
        fields = ['id', 'amount', 'period', 'member']

class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ['id', 'period']

class MovementSerializer(serializers.ModelSerializer):
    period = serializers.PrimaryKeyRelatedField(read_only=True)
    proportionalAmount = serializers.SerializerMethodField()
    member = MemberSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Movement
        fields = ['id', 'amount', 'date', 'member', 'category', 'category_id', 'description', 'period', 'proportionalAmount', 'created_at', 'updated_at']
        read_only_fields = ['member', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Get the current user's member instance
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            member = Member.objects.get(user=request.user)
            validated_data['member'] = member

        #Checks if period exists, otherwise creates it
        movement_date = validated_data.get('date')
        period_str = movement_date.strftime('%Y-%m')
        period, created = Period.objects.get_or_create(period=period_str)
        validated_data['period'] = period

        # Handle description (can be null)
        description = validated_data.get('description')
        if description is not None and description.strip() == '':
            validated_data['description'] = None

        return super().create(validated_data)
    
    def get_proportionalAmount(self, movement):
        current_period = movement.period

        # Find the previous period by subtracting one month
        current_period_date = datetime.strptime(current_period.period, "%Y-%m")
        previous_period_date = current_period_date.replace(day=1) - timedelta(days=1)
        previous_period_str = previous_period_date.strftime("%Y-%m")

        # Find the previous period in the Period model
        try:
            previous_period = Period.objects.get(period=previous_period_str)
        except Period.DoesNotExist:
            # If the previous period doesn't exist, return an empty list
            return []
        
        category = movement.category
        is_prorrata = category.distribution_type.name == 'prorrata'

        # Get all salaries for the members for the given period (by period ID)
        salaries = Salary.objects.filter(period=previous_period)
        total_salary = salaries.aggregate(Sum('amount'))['amount__sum']
        
        proportional_data = []

        for salary in salaries:
            if is_prorrata:
                proportion = salary.amount / total_salary if total_salary > 0 else 0
            else:
                # For equal distribution, set proportion to 0.5
                proportion = 0.5

            proportional_amount = movement.amount * proportion
            proportional_data.append({
                'memberId': salary.member.id,
                'proportion': proportion,
                'amount': proportional_amount
            })
        
        return proportional_data

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user