from django.shortcuts import render , redirect 
from library_db.models import Book, Genre, Language
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
    if request.method == 'POST':
        # --- Retrieve data from the form ---
        title = request.POST.get('title')
        author = request.POST.get('author')
        isbn = request.POST.get('isbn')
        total_copies = request.POST.get('total_copies')
        description = request.POST.get('description')
        
        # --- Handle Language (Get or Create) ---
        language_name = request.POST.get('language')
        # This one line finds the language if it exists, or creates it if it doesn't.
        language_obj, _ = Language.objects.get_or_create(language_name=language_name.strip())

        # --- Create the Book instance ---
        # Note: available_copies is set to total_copies automatically for a new book.
        book = Book.objects.create(
            title=title,
            author=author,
            isbn=isbn,
            language=language_obj,
            description=description,
            total_copies=total_copies,
            available_copies=total_copies # New book starts with all copies available
        )
        
        # --- Handle Genres (Comma-separated list) ---
        genres_string = request.POST.get('genres')
        # Split the string by commas, strip whitespace from each, and filter out any empty strings
        genre_names = [name.strip() for name in genres_string.split(',') if name.strip()]
        
        for name in genre_names:
            # For each genre name, get it if it exists or create a new one
            genre_obj, _ = Genre.objects.get_or_create(genre_name=name)
            # Add the genre to the book's ManyToMany relationship
            book.genre.add(genre_obj)
            
        return redirect('books')
    
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