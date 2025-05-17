from django.shortcuts import render
from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Movement, Member, Category, Distribution_type, Salary, Period, Household
from .serializers import MovementSerializer, MemberSerializer, CategorySerializer, DistributionTypeSerializer, SalarySerializer, PeriodSerializer, UserSerializer, HouseholdSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

class MovementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MovementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['period', 'category']
    
    def get_queryset(self):
        member = self.request.user.member
        if not member.household:
            return Movement.objects.none()
        return Movement.objects.filter(member__household=member.household)

class MemberViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MemberSerializer

    def get_queryset(self):
        member = self.request.user.member
        if not member.household:
            return Member.objects.none()
        return Member.objects.filter(household=member.household)

    @action(detail=False, methods=['get'])
    def me(self, request):
        try:
            member = request.user.member
            serializer = self.get_serializer(member)
            return Response(serializer.data)
        except Member.DoesNotExist:
            return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        member = Member.objects.get(user=self.request.user)
        if not member.household:
            return Category.objects.none()
        return Category.objects.filter(household=member.household)

    def perform_create(self, serializer):
        member = Member.objects.get(user=self.request.user)
        if not member.household:
            raise ValidationError("You must belong to a household to create categories")
        serializer.save(household=member.household)

class DistributionTypeViewSet(viewsets.ModelViewSet):
    queryset = Distribution_type.objects.all()
    serializer_class = DistributionTypeSerializer

class SalaryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SalarySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['period']

    def get_queryset(self):
        member = self.request.user.member
        if not member.household:
            return Salary.objects.none()
        return Salary.objects.filter(member__household=member.household)

class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer

class HouseholdViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = HouseholdSerializer

    def get_queryset(self):
        return Household.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        household = serializer.save()
        member = self.request.user.member
        member.household = household
        member.save()
        household.members.add(self.request.user)

class JoinHouseholdView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HouseholdSerializer

    def post(self, request, *args, **kwargs):
        household_name = request.data.get('name')
        try:
            household = Household.objects.get(name=household_name)
            member = request.user.member
            member.household = household
            member.save()
            household.members.add(request.user)
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except Household.DoesNotExist:
            return Response({'error': 'Household not found'}, status=status.HTTP_404_NOT_FOUND)

class UserCreate(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()  # Capture the returned user
            Member.objects.create(user=user, name=user.username)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)