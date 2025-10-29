from django.shortcuts import render , redirect, get_object_or_404
from library_db.models import Book, Genre, Language, User
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.cache import cache
from functools import reduce
from django.http import JsonResponse
from django.template.loader import render_to_string
import pickle

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
        'all_genres': Genre.objects.all().order_by('genre_name'),
        'all_languages': Language.objects.all().order_by('language_name'),
    }
    return render(request, 'admin/books.html', context)

class TrieNode:
    def __init__(self):
        self.children = {}
        self.book_ids = set()

class Trie:
    def __init__(self):
        self.root = TrieNode()
    def insert(self, word, book_id):
        # ... (methods are needed for unpickling but not used in the view)
        pass
    def search_prefix(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children: return set()
            node = node.children[char]
        return self._collect_all_ids_from_node(node)
    def _collect_all_ids_from_node(self, node):
        ids = set(node.book_ids)
        for child_node in node.children.values():
            ids.update(self._collect_all_ids_from_node(child_node))
        return ids
    
# New API view to handle live search requests from JavaScript
def filter_books(request):
    queryset = Book.objects.all().order_by('title')
    
    search_query = request.GET.get('search', '').lower().strip()
    genre_id = request.GET.get('genre', '')
    language_id = request.GET.get('language', '')
    
    # --- UPDATED DSA LOGIC: Use the Trie for prefix search ---
    if search_query:
        pickled_trie = cache.get('book_trie_index')
        if pickled_trie:
            trie = pickle.loads(pickled_trie)
            matching_ids = trie.search_prefix(search_query)
            if matching_ids:
                queryset = queryset.filter(pk__in=matching_ids)
            else:
                queryset = queryset.none() # No results if prefix not found
        else:
            # Fallback to a simple contains search if Trie isn't built
            queryset = queryset.filter(title__icontains=search_query)

    # Genre and Language filters remain the same
    if genre_id:
        queryset = queryset.filter(genre__pk=genre_id)
    if language_id:
        queryset = queryset.filter(language__pk=language_id)

    # Pagination and response logic remains the same
    page_number = request.GET.get('page', 1)
    paginator = Paginator(queryset, 8)
    page_obj = paginator.get_page(page_number)
    books_html = render_to_string('partials/book_grid_content.html', {'books_page': page_obj})
    return JsonResponse({'books_html': books_html})


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
    return render(request, 'users/browse.html', context)

def myBooks(request):
    return render(request, 'users/books.html')

def myRequests(request):
    return render(request, 'users/requests.html')

def details(request, book_id):
    book = get_object_or_404(Book, book_id=book_id)
    return render(request, 'details/details.html', {'book': book})

def user_login(request):
    return render(request, 'auth/user_login.html')

def user_signup(request):
    if request.method == 'POST':
        # Handle user signup logic here
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password') 

        if not (name and phone and email and password):
            error_message = "All fields are required."
            return render(request, 'auth/user_signup.html', {'error_message': error_message})
        
        if User.objects.filter(Q(email = email) | Q(phone = phone)).exists():
            error_message = "A user with this email or phone number already exists."
            return render(request, 'auth/user_signup.html', {'error_message': error_message})
        
        user = User.objects.create(
            name = name,
            phone = phone,
            email = email,
            password = password
        )

        messages.success(request, "Registration successful. You are now logged in.")
        return redirect('userDashboard')
    return render(request, 'auth/user_signup.html')

def admin_login(request):
    return render(request, 'auth/admin_login.html')