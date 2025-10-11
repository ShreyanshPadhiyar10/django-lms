
from django.contrib import admin
from .models import Admin, Genre, Book, User, IssueRecord, Request, WaitingList, Language

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('admin_id', 'name', 'email')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('genre_id', 'genre_name')


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('language_id', 'language_name')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'isbn', 'title', 'author', 'genre_display', 'language', 'image_url', 'total_copies', 'available_copies')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('genre',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name', 'email', 'phone')
    search_fields = ('name', 'email')


@admin.register(IssueRecord)
class IssueRecordAdmin(admin.ModelAdmin):
    list_display = ('issue_id', 'user', 'book', 'issue_date', 'due_date', 'return_date', 'status')
    list_filter = ('status', 'issue_date')
    search_fields = ('user__name', 'book__title')


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'user', 'book', 'request_date', 'status')
    list_filter = ('status',)
    search_fields = ('user__name', 'book__title')


@admin.register(WaitingList)
class WaitingListAdmin(admin.ModelAdmin):
    list_display = ('waiting_id', 'user', 'book', 'position', 'request_date')
    list_filter = ('book',)
    search_fields = ('user__name', 'book__title')
