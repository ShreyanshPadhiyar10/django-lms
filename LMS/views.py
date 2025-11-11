from django.shortcuts import render, redirect, get_object_or_404
from library_db.models import Book, Genre, Language , Request, IssueRecord, WaitingList
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Max
from functools import wraps
from django.contrib import messages
from django.contrib.auth import logout, get_user_model
from django.contrib.auth import authenticate, login as auth_login
from django.core.paginator import Paginator
from django.core.cache import cache
from django.http import JsonResponse
from django.template.loader import render_to_string
from datetime import date, timedelta
import pickle
User = get_user_model()


def home(request):
    return redirect('user_login')

@staff_member_required
def admin_dashboard(request):
    total_books = Book.objects.count()
    total_users = User.objects.count()

    context = {
        'total_books': total_books,
        'total_users': total_users,
    }
    return render(request, 'admin/dashboard.html', context)

@staff_member_required
def admin_books(request):
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

@staff_member_required
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
            
        return redirect('admin_books')
    
    return render(request, 'admin/add_book.html')

@staff_member_required
def admin_edit_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        isbn = request.POST.get('isbn')
        total_copies = request.POST.get('total_copies')
        description = request.POST.get('description')
        language_name = request.POST.get('language')

        # Find or create language (same logic as add)
        language_obj, _ = Language.objects.get_or_create(language_name=language_name.strip())

        # Update the book fields
        book.title = title
        book.author = author
        book.isbn = isbn
        book.language = language_obj
        book.description = description
        book.total_copies = total_copies
        book.available_copies = total_copies  # same logic as add
        book.save()

        # Update genres
        genres_string = request.POST.get('genres')
        genre_names = [name.strip() for name in genres_string.split(',') if name.strip()]

        # Clear existing genres and re-add (so it works like "replace")
        book.genre.clear()
        for name in genre_names:
            genre_obj, _ = Genre.objects.get_or_create(genre_name=name)
            book.genre.add(genre_obj)

        return redirect('admin_books')

    # Pre-fill existing data for form
    existing_genres = ', '.join([genre.genre_name for genre in book.genre.all()])

    context = {
        'book': book,
        'prefill': {
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn or '',
            'language': book.language.language_name if book.language else '',
            'genres': existing_genres,
            'total_copies': book.total_copies,
            'description': book.description or '',
        }
    }

    return render(request, 'admin/edit_book.html', context)

def admin_delete_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    book.delete()
    messages.success(request, f'"{book.title}" has been deleted successfully.')
    return redirect('admin_books')
@staff_member_required
def admin_issue_receive(request):
    return render(request, 'admin/issue_receive.html')

@staff_member_required
def admin_users(request):
    users = User.objects.all().order_by('username')

    context = {
        'users' : users,
        'total_users': users.count()
    }
    return render(request, 'admin/users.html', context)

@staff_member_required
def admin_requests(request):
    pending_requests = Request.objects.filter(status='pending').select_related('user', 'book').order_by('-request_date')
    approved_requests = Request.objects.filter(status='approved').select_related('user', 'book').order_by('-request_date')
    rejected_requests = Request.objects.filter(status='rejected').select_related('user', 'book').order_by('-request_date')

    context = {
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
    }
    return render(request, 'admin/requests.html', context)

@staff_member_required
def admin_settings(request):
    return render(request, 'admin/settings.html')

@login_required
def user_dashboard(request):
    return render(request, 'users/dashboard.html')

@login_required
def user_browse(request):
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

@login_required
def request_book(request, book_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
    
    user = request.user
    print(f"DEBUG: Final User object: {user} (ID: {user.pk})")

    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Please log in to request books.'}, status=401)

    book = get_object_or_404(Book, pk=book_id)
    

    # 1. Check if user already has this book issued
    if IssueRecord.objects.filter(book=book, user=user, status__in=['issued', 'overdue']).exists():
        return JsonResponse({
            'status': 'error', 
            'message': 'You already have this book issued.'
        }, status=400)

    # 2. Check if user is already on the waiting list
    if WaitingList.objects.filter(book=book, user=user).exists():
        return JsonResponse({
            'status': 'error', 
            'message': 'You are already on the waiting list for this book.'
        }, status=400)

    # 3. Process the request
    if book.available_copies > 0:
        # --- Book is Available: Create an IssueRecord ---
        book.available_copies -= 1
        book.save()

        newissue = IssueRecord.objects.create(
            user=user,
            book=book,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=14), # 2-week loan period
            status='issued'
        )
        print("new issue created successfully ",newissue)
        return JsonResponse({
            'status': 'success', 
            'message': 'Book issued successfully! It has been added to your profile.',
            'new_copies': book.available_copies
        })
    else:
        # --- Book is Unavailable: Add to WaitingList (Priority Queue) ---
        
        # Find the next position in the queue for this specific book
        current_max_pos = WaitingList.objects.filter(book=book).aggregate(Max('position'))
        new_pos = (current_max_pos['position__max'] or 0) + 1
        
        newList = WaitingList.objects.create(
            user=user,
            book=book,
            position=new_pos
        )
        print("new waiting list created successfully ",newList)
        
        return JsonResponse({
            'status': 'waiting', 
            'message': 'This book is unavailable. You have been added to the waiting list.'
        })

@login_required
def user_my_books(request):
    issued_books = IssueRecord.objects.filter(user__email =request.user.email).select_related('book')
    user_request = Request.objects.filter(user=request.user).select_related('book')

    context = {
        'issued_books': issued_books,
        'user_request': user_request,
    }
    return render(request, 'users/books.html', context)

@login_required
def user_my_requests(request):
    return render(request, 'users/requests.html')

@staff_member_required
def admin_book_details(request, book_id):
    book = get_object_or_404(Book, book_id=book_id)
    return render(request, 'admin/book_details.html', {'book': book})

@login_required
def user_book_details(request, book_id):
    book = get_object_or_404(Book, book_id=book_id)
    return render(request, 'users/book_details.html', {'book': book})

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not (email and password):
            messages.error(request, "Please enter email address and password.")
            return render(request, 'auth/user_login.html')
        
        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Welcome back!")
            
            # Redirect based on their role
            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            messages.error(request, "Invalid credentials.")
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
        
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name,
                phone=phone
            )
            # Log them in immediately
            auth_login(request, user)
            messages.success(request, "Registration successful. You are now logged in.")
            return redirect('user_dashboard')

        except Exception as e:
            messages.error(request, f"An error occurred during signup: {e}")
            return render(request, 'auth/user_signup.html')

    return render(request, 'auth/user_signup.html')

# def admin_login(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')

#         if not (email and password):
#             messages.error(request, "Please enter both email and password")
#             return render(request, 'auth/admin_login.html')
        
#         try:
#             admin = Admin.objects.get(email=email)
#         except Admin.DoesNotExist:
#             messages.error(request, "Invalid Credentials. Please try again.")
#             return render(request, 'auth/admin_login.html')
        
#         if password == admin.password:
#             request.session['admin_id'] = admin.admin_id
#             request.session['admin_name'] = admin.name
#             request.session.set_expiry(60 * 60 * 24 * 7)
#             messages.success(request, f"Welcome back, {admin.name}!")
#             return redirect('admin_dashboard')
#         else:
#             messages.error(request, "Invalid credentials.")
#             return render(request, 'auth/admin_login.html')
#     return render(request, 'auth/admin_login.html')

@login_required
def user_logout(request):
    logout(request)  
    return redirect('user_login')  

@staff_member_required
def admin_logout(request):
    logout(request)
    return redirect('user_login') 