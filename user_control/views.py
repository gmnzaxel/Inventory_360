from django.shortcuts import render
from rest_framework import viewsets
from .serializer import *
from ..control.models import *



class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

