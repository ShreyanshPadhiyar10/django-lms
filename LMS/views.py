from django.shortcuts import render  
from library_db.models import Book 
from django.core.paginator import Paginator

def home(request):
    return render(request, 'admin/dashboard.html')

def dashboard(request):
    return render(request, 'admin/dashboard.html')

def books(request):
    all_books_list = Book.objects.all().order_by('title')
    
    # Create a Paginator object with 8 books per page. You can change this number.
    paginator = Paginator(all_books_list, 8) 

    # Get the current page number from the URL's query parameters (e.g., /books/?page=2)
    page_number = request.GET.get('page')
    
    # Get the Page object for the requested page number
    books_page_obj = paginator.get_page(page_number)
    
    context = {
        'books_page': books_page_obj,
    }
    return render(request, 'admin/books.html', context)

def add_book(request):
    return render(request, 'admin/add_book.html')

def issue_receive(request):
    return render(request, 'admin/issue_receive.html')

def users(request):
    return render(request, 'admin/users.html')

def requests(request):
    return render(request, 'admin/requests.html')

def settings(request):
    return render(request, 'admin/settings.html')

def userDashboard(request):
    return render(request, 'users/dashboard.html')

def browse(request):
    return render(request, 'users/browse.html')

def myBooks(request):
    return render(request, 'users/books.html')

def myRequests(request):
    return render(request, 'users/requests.html')

def details(request):
    return render(request, 'details/details.html')