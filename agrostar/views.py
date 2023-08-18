from django.shortcuts import render
from store.models import Product, ReviewRating, ReviewRating
from category.models import Category
from chat.models import ChatModel
from django.db.models import Q

def home(request):
    products = Product.objects.all().filter(is_availible=True).order_by('created_date')[:4]
    kategorije = Category.objects.all().order_by('category_name')
    message_objs = 0
    #Dohvati recenzije
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)
    
    if request.user.is_authenticated:
        message_objs = ChatModel.objects.filter(Q(sender=request.user) | Q(receiver=request.user.id)).count()
    else:
        pass
    context ={
        'products': products,
        'reviews':reviews,
        'kategorije':kategorije,
        'broj_por':message_objs,
    }
    return render(request, 'home.html', context)

def uputstva(request):
    return render(request, 'uputstva.html')