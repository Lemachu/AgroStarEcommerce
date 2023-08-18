from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),
    path('category/<slug:category_slug>/<int:product_id>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('submit_review/<int:product_id>/',views.submit_review, name='submit_review'),
    path('dodaj_proizvod/', views.dodaj_proizvod, name='dodaj_proizvod'),
    path('update_proizvod/<int:proizvod_id>/',views.update_proizvod, name='update_proizvod'),
    path('obrisi/<int:proizvod_id>/',views.obrisi, name='obrisi'),
    path('sakrij_komentar/<int:komentar_id>/',views.sakrij_komentar, name='sakrij_komentar'),
    path('galerija_dodaj/<int:proizvod_id>/',views.galerija_dodaj, name='galerija_dodaj'),
] 