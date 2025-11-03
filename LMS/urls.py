"""
URL configuration for LMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('books/', views.books, name='books'),
    path('books/<int:book_id>/', views.details_admin, name='details_admin'),
    path('add_book/', views.add_book, name='add_book'),
    path('issue_receive/', views.issue_receive, name='issue_receive'),
    path('users/', views.users, name='users'),
    path('requests/', views.requests, name='requests'),
    path('settings/', views.settings, name='settings'),
    path('api/filter-books/', views.filter_books, name='filter_books'),

    path('user/dashboard/', views.userDashboard, name='userDashboard'),
    path('user/books', views.myBooks, name='myBooks'),
    path('user/requests', views.myRequests, name='myRequests'),
    path('user/browse', views.browse, name='browse'),
    path('user/browse/book/<int:book_id>/', views.details_user, name='details_user'),

    path('user/login', views.user_login, name='user_login'),
    path('user/signup', views.user_signup, name='user_signup'),
    path('admin_login', views.admin_login, name='admin_login'),

    path('user/logout', views.user_logout, name='user_logout'),
    path('admin_logout', views.admin_logout, name='admin_logout'),
]
