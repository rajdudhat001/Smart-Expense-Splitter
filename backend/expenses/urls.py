from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('groups/', views.group_list_view, name='group_list'),
    path('groups/create/', views.group_create_view, name='group_create'),
    path('groups/<int:pk>/update/', views.group_update_view, name='group_update'),
    path('groups/<int:pk>/delete/', views.group_delete_view, name='group_delete'),
    
    # Group Member Management URLs
    path('groups/<int:group_pk>/members/', views.member_list_view, name='member_list'),
    path('groups/<int:group_pk>/members/add/', views.member_create_view, name='member_create'),
    path('groups/<int:group_pk>/members/<int:member_pk>/update/', views.member_update_view, name='member_update'),
    path('groups/<int:group_pk>/members/<int:member_pk>/delete/', views.member_delete_view, name='member_delete'),

    # Expense Management URLs
    path('groups/<int:group_pk>/expenses/', views.expense_list_view, name='expense_list'),
    path('groups/<int:group_pk>/expenses/add/', views.expense_create_view, name='expense_create'),
    path('groups/<int:group_pk>/expenses/<int:expense_pk>/', views.expense_detail_view, name='expense_detail'),
    path('groups/<int:group_pk>/expenses/<int:expense_pk>/update/', views.expense_update_view, name='expense_update'),
    path('groups/<int:group_pk>/expenses/<int:expense_pk>/delete/', views.expense_delete_view, name='expense_delete'),
]


