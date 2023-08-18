from django.urls import path
from . import views

urlpatterns = [
    path('poruke/', views.poruke, name='poruke'),
    path('<str:username>/', views.chatPage, name='chat'),
    path('poruke/<int:user_id>', views.poruke, name='poruke'),
]