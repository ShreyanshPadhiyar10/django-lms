from django.http import HttpResponse
from django.shortcuts import render   

def home(request):
    return render(request, 'admin/dashboard.html')

def dashboard(request):
    return render(request, 'admin/dashboard.html')

def books(request):
    return render(request, 'admin/books.html')

def add_book(request):
    return render(request, 'admin/add_book.html')

def issue_return(request):
    return render(request, 'admin/issue_return.html')

def users(request):
    return render(request, 'admin/users.html')

def requests(request):
    return render(request, 'admin/requests.html')

def settings(request):
    return render(request, 'admin/settings.html')