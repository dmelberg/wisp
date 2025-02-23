from django.shortcuts import render
from rest_framework import viewsets
from .models import Movement, Member, Category, Distribution_type, Salary, Period
from .serializers import MovementSerializer, MemberSerializer, CategorySerializer, DistributionTypeSerializer, SalarySerializer, PeriodSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class RegisterView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to register
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if username and password:
            user = User.objects.create_user(username=username, password=password)
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)

class MovementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Movement.objects.all()
    serializer_class = MovementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['period', 'category']

class MemberViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class DistributionTypeViewSet(viewsets.ModelViewSet):
    queryset = Distribution_type.objects.all()
    serializer_class = DistributionTypeSerializer

class SalaryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer

class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer