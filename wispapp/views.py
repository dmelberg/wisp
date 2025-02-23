from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Movement, Member, Category, Distribution_type, Salary, Period
from .serializers import MovementSerializer, MemberSerializer, CategorySerializer, DistributionTypeSerializer, SalarySerializer, PeriodSerializer, UserSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User

class MovementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MovementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['period', 'category']
    
    def get_queryset(self):
        member = self.request.user.member
        household = member.household.first()
        return Movement.objects.filter(member__household=household)

class MemberViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MemberSerializer

    def get_queryset(self):
        member = self.request.user.member
        household = member.household.first()
        return Member.objects.filter(household=household)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

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
        household = member.household.first()
        return Salary.objects.filter(member__household=household)

class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer

class UserCreate(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs): #use post method to access request data.
        serializer = self.get_serializer(data=request.data) #create an instance of the serializer.

        if serializer.is_valid(): #validate the data
            serializer.save() #save the data.
            Member.objects.create(user=user, name=user.username)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)