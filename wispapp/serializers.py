from rest_framework import serializers
from .models import Movement, Member, Category, Distribution_type, Salary, Period, Household, MovementDistribution
from django.db.models import Sum
from datetime import datetime, timedelta
from django.contrib.auth.models import User

class HouseholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Household
        fields = ['id', 'name']

class MemberSerializer(serializers.ModelSerializer):
    household = HouseholdSerializer(read_only=True)
    total_owed = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_paid = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Member
        fields = ['id', 'name', 'household', 'total_owed', 'total_paid', 'balance']

class DistributionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distribution_type
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    distribution_type = DistributionTypeSerializer(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'household', 'distribution_type', 'created_at', 'updated_at']
        read_only_fields = ['household', 'created_at', 'updated_at']

class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ['id', 'period']

class SalarySerializer(serializers.ModelSerializer):
    period = PeriodSerializer(read_only=True)
    member = MemberSerializer(read_only=True)
    period_id = serializers.PrimaryKeyRelatedField(
        queryset=Period.objects.all(),
        source='period',
        write_only=True
    )
    member_id = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(),
        source='member',
        write_only=True
    )

    class Meta: 
        model = Salary
        fields = ['id', 'amount', 'period', 'member', 'period_id', 'member_id']

    def create(self, validated_data):
        # Get the current user's member instance to verify household access
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            current_member = Member.objects.get(user=request.user)
            member = validated_data.get('member')
            
            # Verify that the member belongs to the same household
            if member.household != current_member.household:
                raise serializers.ValidationError("You can only create salaries for members in your household")
            
            return super().create(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Get the current user's member instance to verify household access
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            current_member = Member.objects.get(user=request.user)
            member = validated_data.get('member', instance.member)
            
            # Verify that the member belongs to the same household
            if member.household != current_member.household:
                raise serializers.ValidationError("You can only update salaries for members in your household")
        
        # Update the salary
        updated_salary = super().update(instance, validated_data)
        
        # Get the household and period
        household = updated_salary.member.household
        period = updated_salary.period
        
        # Get all prorrata movements in this period for this household
        prorrata_movements = Movement.objects.filter(
            member__household=household,
            period=period,
            category__distribution_type__name='prorrata'
        )
        
        # Get total household salary for the period
        total_salary = Salary.objects.filter(
            member__household=household,
            period=period
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        if total_salary == 0:
            return updated_salary
        
        # Update distributions for each movement
        for movement in prorrata_movements:
            # Delete existing distributions
            MovementDistribution.objects.filter(movement=movement).delete()
            
            # Get all household members
            household_members = Member.objects.filter(household=household)
            
            # Create new distributions based on updated salary proportions
            for household_member in household_members:
                member_salary = Salary.objects.filter(
                    member=household_member,
                    period=period
                ).first()
                
                if not member_salary:
                    continue
                
                # Calculate new proportional share
                share_amount = (member_salary.amount / total_salary) * movement.amount
                
                MovementDistribution.objects.create(
                    movement=movement,
                    member=household_member,
                    amount=share_amount,
                    is_payer=(household_member == movement.member)
                )
        
        return updated_salary

class MovementSerializer(serializers.ModelSerializer):
    period = serializers.PrimaryKeyRelatedField(read_only=True)
    member = MemberSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Movement
        fields = ['id', 'amount', 'date', 'member', 'category', 'category_id', 'description', 'period', 'created_at', 'updated_at']
        read_only_fields = ['member', 'created_at', 'updated_at']

    def get_previous_period(self, current_period):
        """Get the previous period based on the current period string (YYYY-MM)"""
        year, month = map(int, current_period.period.split('-'))
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        previous_period_str = f"{year:04d}-{month:02d}"
        return Period.objects.get_or_create(period=previous_period_str)[0]

    def create(self, validated_data):
        # Get the current user's member instance
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError("User context is required")
        
        member = Member.objects.get(user=request.user)
        validated_data['member'] = member
        
        # Infer period from date
        movement_date = validated_data['date']
        period_str = movement_date.strftime('%Y-%m')
        
        # Get or create the period
        period, created = Period.objects.get_or_create(period=period_str)
        validated_data['period'] = period
        
        # Create the movement
        movement = super().create(validated_data)
        
        # Get all members in the household
        household_members = Member.objects.filter(household=member.household)
        total_members = household_members.count()
        
        # Get the distribution type
        distribution_type = movement.category.distribution_type.name
        
        if distribution_type == 'equal':
            # Equal distribution: divide amount equally among all members
            share_amount = movement.amount / total_members
            for household_member in household_members:
                MovementDistribution.objects.create(
                    movement=movement,
                    member=household_member,
                    amount=share_amount,
                    is_payer=(household_member == member)
                )
                
        elif distribution_type == 'prorrata':
            # Get the previous period for salary calculations
            previous_period = self.get_previous_period(period)
            
            # Get total household salary for the previous period
            total_salary = Salary.objects.filter(
                member__household=member.household,
                period=previous_period
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            if total_salary == 0:
                raise serializers.ValidationError(f"Cannot create prorrata distribution: no salaries found for the previous period ({previous_period.period})")
            
            # Create distribution based on salary proportions from previous period
            for household_member in household_members:
                member_salary = Salary.objects.filter(
                    member=household_member,
                    period=previous_period
                ).first()
                
                if not member_salary:
                    raise serializers.ValidationError(f"No salary found for member {household_member.name} in the previous period ({previous_period.period})")
                
                # Calculate proportional share
                share_amount = (member_salary.amount / total_salary) * movement.amount
                
                MovementDistribution.objects.create(
                    movement=movement,
                    member=household_member,
                    amount=share_amount,
                    is_payer=(household_member == member)
                )
        else:
            raise serializers.ValidationError(f"Unknown distribution type: {distribution_type}")
        
        return movement

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class MovementDistributionSerializer(serializers.ModelSerializer):
    movement = MovementSerializer(read_only=True)
    member = MemberSerializer(read_only=True)

    class Meta:
        model = MovementDistribution
        fields = ['id', 'movement', 'member', 'amount', 'is_payer', 'created_at', 'updated_at']