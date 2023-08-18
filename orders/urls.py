from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('placanje_preuzecem/<int:order_num>', views.placanje_preuzecem, name='placanje_preuzecem'),
    path('licno_preuzimanje/', views.licno_preuzimanje, name='licno_preuzimanje'),
]