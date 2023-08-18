from http.client import HTTPResponse
from django.shortcuts import render, get_object_or_404, redirect
from category.models import Category
from .models import Product, ProductGallery, ReviewRating
from carts.views import _cart_id, CartItem
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.db.models import Q
from .forms import ReviewForm, dodajProizvodForm
from django.contrib import messages
from orders.models import OrderProduct
from accounts.models import Account, UserProfile
from django.utils.text import slugify
import random
# Create your views here.

def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug!=None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_availible=True).order_by('product_name')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_availible=True).order_by('product_name')
        paginator = Paginator(products, 9)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context ={
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_id):
    trenutni = None
    
    try:
        single_product = Product.objects.get(category__slug=category_slug, id=product_id)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    if request.user.is_authenticated:
        trenutni = request.user.id
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None
    #Dohvati recenzije
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    
    #dohvati product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    
    userprofile = get_object_or_404(UserProfile, user=single_product.prodavac)
    
    context = {
        'single_product':single_product,
        'in_cart':in_cart,
        'orderproduct':orderproduct,
        'reviews':reviews,
        'trenutni':trenutni,
        'product_gallery':product_gallery,
        'userprofile':userprofile,
    }
    return render(request, 'store/product_detail.html',context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword)|Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products':products,
        'product_count':product_count,
    }
    return render(request, 'store/store.html', context)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Hvala Vam! Vaša recenzija je ažurirana.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Hvala Vam! Vaša recenzija je dostavljena.')
                return redirect(url)

def sakrij_komentar(request, komentar_id):
    url = request.META.get('HTTP_REFERER')
    komentar_id=int(komentar_id)
    try:
        komentar = ReviewRating.objects.get(id=komentar_id)
    except:
        return redirect('dashboard')
    komentar.status=False
    komentar.delete()
    messages.success(request, 'Komentar obrisan!')
    return redirect(url)


def dodaj_proizvod(request):
    user_id = request.user
    form = dodajProizvodForm()
    if request.method == 'POST':
        form = dodajProizvodForm(request.POST, request.FILES, initial={'prodavac': 'user_id'})
        if form.is_valid():
            product_name=form.cleaned_data['product_name']
            slug = form.cleaned_data['product_name']
            description = form.cleaned_data['description']
            price = form.cleaned_data['price']
            images = form.cleaned_data['images']
            stock = form.cleaned_data['stock']
            is_availible = form.cleaned_data['is_availible']
            category = form.cleaned_data['category']
            prodavac = request.user
            mjera = form.cleaned_data['mjera']
            slug = form.cleaned_data['product_name']
            proizvod = Product()
            proizvod.product_name=product_name
            proizvod.slug=random.randrange(100, 9999)
            proizvod.description=description
            proizvod.price=price
            proizvod.images=images
            proizvod.stock=stock
            proizvod.is_availible=is_availible
            proizvod.prodavac=prodavac
            proizvod.mjera=mjera
            proizvod.category=category
            proizvod.save(proizvod)
            messages.success(request, 'Proizvod uspjesno dodan')
            return redirect('moja_trgovina')
        
    context = {
        'forms':form,
    }
    return render(request, 'accounts/dodaj_proizvod.html',context)

def update_proizvod(request, proizvod_id):
    proizvod_id=int(proizvod_id)
    try:
        proizvod_shelf = Product.objects.get(id=proizvod_id)
    except Product.DoesNotExist:
        return redirect('dashboard')
    proizvod_form = dodajProizvodForm(request.POST or None, instance = proizvod_shelf)
    if proizvod_form.is_valid():
        proizvod_form.save()
        return redirect('moja_trgovina')
    else:
        pass
    context = {
        'forms':proizvod_form,
        'proizvod_id':proizvod_id,
    }
    return render(request, 'accounts/update_proizvod.html',context)

def obrisi(request, proizvod_id):
    proizvod_id=int(proizvod_id)
    try:
        proizvod_shelf = Product.objects.get(id=proizvod_id)
    except:
        return redirect('dashboard')
    proizvod_shelf.delete()
    return redirect('moja_trgovina')



def galerija_dodaj(request, proizvod_id):
    url = request.META.get('HTTP_REFERER')
    product_id=int(proizvod_id)
    proizvod=Product.objects.get(id=product_id)
    if request.method == "POST":
        images = request.FILES.getlist('images')

        for image in images:
            ProductGallery.objects.create(product=proizvod,image=image)
        
        
    images = ProductGallery.objects.all()
    return redirect(url)
    