from django.shortcuts import render , redirect, get_object_or_404
from library_db.models import Book, Genre, Language, User, Admin
from django.db.models import Q
from functools import wraps
from django.contrib import messages
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.core.cache import cache
from functools import reduce
from django.http import JsonResponse
from django.template.loader import render_to_string
import pickle

def user_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('user_login')
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_id'):
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper

def login_required_any(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not (request.session.get('user_id') or request.session.get('admin_id')):
            return redirect('user_login')
        return view_func(request, *args, **kwargs)
    return wrapper

def home(request):
    return redirect('user_login')

@admin_login_required
def admin_dashboard(request):
    total_books = Book.objects.count()
    total_users = User.objects.count()

    context = {
        'total_books': total_books,
        'total_users': total_users,
    }
    return render(request, 'admin/dashboard.html', context)

@admin_login_required
def admin_books(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    all_books_list = Book.objects.all().order_by('title')
    
    paginator = Paginator(all_books_list, 8) 

    page_number = request.GET.get('page')
    
    books_page_obj = paginator.get_page(page_number)
    
    context = {
        'books_page': books_page_obj,
        'all_genres': Genre.objects.all().order_by('genre_name'),
        'all_languages': Language.objects.all().order_by('language_name'),
        'user_type': 'admin',
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
    
def filter_books(request):
    queryset = Book.objects.all().order_by('title')
    
    search_query = request.GET.get('search', '').lower().strip()
    genre_id = request.GET.get('genre', '')
    language_id = request.GET.get('language', '')
    
    if search_query:
        pickled_trie = cache.get('book_trie_index')
        if pickled_trie:
            trie = pickle.loads(pickled_trie)
            matching_ids = trie.search_prefix(search_query)
            if matching_ids:
                queryset = queryset.filter(pk__in=matching_ids)
            else:
                queryset = queryset.none() 
        else:
            queryset = queryset.filter(title__icontains=search_query)

    if genre_id:
        queryset = queryset.filter(genre__pk=genre_id)
    if language_id:
        queryset = queryset.filter(language__pk=language_id)

    page_number = request.GET.get('page', 1)
    paginator = Paginator(queryset, 8)
    page_obj = paginator.get_page(page_number)
    books_html = render_to_string('partials/book_grid_content.html', {'books_page': page_obj})
    return JsonResponse({'books_html': books_html})

@admin_login_required
def admin_add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        isbn = request.POST.get('isbn')
        total_copies = request.POST.get('total_copies')
        description = request.POST.get('description')
        
        language_name = request.POST.get('language')
        # This one line finds the language if it exists, or creates it if it doesn't.
        language_obj, _ = Language.objects.get_or_create(language_name=language_name.strip())

        book = Book.objects.create(
            title=title,
            author=author,
            isbn=isbn,
            language=language_obj,
            description=description,
            total_copies=total_copies,
            available_copies=total_copies 
        )
        
        genres_string = request.POST.get('genres')
        genre_names = [name.strip() for name in genres_string.split(',') if name.strip()]
        
        for name in genre_names:
            genre_obj, _ = Genre.objects.get_or_create(genre_name=name)
            book.genre.add(genre_obj)
            
        return redirect('books')
    
    return render(request, 'admin/add_book.html')

@admin_login_required
def admin_issue_receive(request):
    return render(request, 'admin/issue_receive.html')

@admin_login_required
def admin_users(request):
    return render(request, 'admin/users.html')

@admin_login_required
def admin_requests(request):
    return render(request, 'admin/requests.html')

@admin_login_required
def admin_settings(request):
    return render(request, 'admin/settings.html')

@user_login_required
def user_dashboard(request):
    return render(request, 'users/dashboard.html')

@user_login_required
def user_browse(request):
    if 'user_id' not in request.session:
        return redirect('user_login')
    
    all_books_list = Book.objects.all().order_by('title')
    
    paginator = Paginator(all_books_list, 8) 

    page_number = request.GET.get('page')
    
    books_page_obj = paginator.get_page(page_number)
    
    context = {
        'books_page': books_page_obj,
        'all_genres': Genre.objects.all().order_by('genre_name'),
        'all_languages': Language.objects.all().order_by('language_name'),
        'user_type': 'user',
    }
    return render(request, 'users/browse.html', context)

@user_login_required
def user_my_books(request):
    return render(request, 'users/books.html')

@user_login_required
def user_my_requests(request):
    return render(request, 'users/requests.html')

@admin_login_required
def admin_book_details(request, book_id):
    book = get_object_or_404(Book, book_id=book_id)
    return render(request, 'admin/book_details.html', {'book': book})

@user_login_required
def user_book_details(request, book_id):
    book = get_object_or_404(Book, book_id=book_id)
    return render(request, 'users/book_details.html', {'book': book})

def user_login(request):
    if request.method == 'POST':
        identifier = request.POST.get('email')
        password = request.POST.get('password')

        if not (identifier and password):
            messages.error(request, "Please enter email address and password.")
            return render(request, 'auth/user_login.html')
        
        try:
            user = User.objects.get(Q(email__iexact=identifier) | Q(phone__iexact=identifier))
        except User.DoesNotExist:
            messages.error(request, "Invalid Credentials. Please try again.")
            return render(request, 'auth/user_login.html')
        
        if password == user.password:
            request.session['user_id'] = user.user_id
            request.session['user_name'] = user.name
            request.session.set_expiry(60 * 60 * 24 * 7)  # optional
            messages.success(request, f"Welcome back, {user.name}!")
            return redirect('user_dashboard')
        else:
            messages.error(request, "Invalid credentials.")
            return render(request, 'auth/user_login.html')
    return render(request, 'auth/user_login.html')

def user_signup(request):
    if request.method == 'POST':
        # Handle user signup logic here
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password') 

        if not (name and phone and email and password):
            messages.error(request, "Please fill all required fields.")
            return render(request, 'auth/user_signup.html')
        
        if User.objects.filter(Q(email = email) | Q(phone = phone)).exists():
            messages.error(request, "User with this email or phone already exists.")
            return render(request, 'auth/user_signup.html')
        
        user = User.objects.create(
            name = name,
            phone = phone,
            email = email,
            password = password
        )

        request.session['user_id'] = user.user_id
        request.session['user_name'] = user.name
        request.session.set_expiry(60 * 60 * 24 * 7)


        messages.success(request, "Registration successful. You are now logged in.")
        return redirect('user_dashboard')
    return render(request, 'auth/user_signup.html')

def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not (email and password):
            messages.error(request, "Please enter both email and password")
            return render(request, 'auth/admin_login.html')
        
        try:
            admin = Admin.objects.get(email=email)
        except Admin.DoesNotExist:
            messages.error(request, "Invalid Credentials. Please try again.")
            return render(request, 'auth/admin_login.html')
        
        if password == admin.password:
            request.session['admin_id'] = admin.admin_id
            request.session['admin_name'] = admin.name
            request.session.set_expiry(60 * 60 * 24 * 7)
            messages.success(request, f"Welcome back, {admin.name}!")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid credentials.")
            return render(request, 'auth/admin_login.html')
    return render(request, 'auth/admin_login.html')

def user_logout(request):
    logout(request)  
    return redirect('user_login')  


def admin_logout(request):
    logout(request)
    return redirect('admin_login') 