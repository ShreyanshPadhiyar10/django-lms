from django.http import HttpResponse
from django.shortcuts import render   

def home(request):
    return render(request, 'admin/dashboard.html')

def dashboard(request):
    return render(request, 'admin/dashboard.html')

def books(request):
    return render(request, 'admin/books.html')