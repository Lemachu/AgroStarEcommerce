from django import forms
from .models import ReviewRating
from store.models import Product, ProductGallery
from category.models import Category
from accounts.models import Account
from requests import request

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject','review', 'rating']

class dodajProizvodForm(forms.ModelForm):
    #prodavac = forms.ModelMultipleChoiceField(queryset=Account.objects.filter(id=request.user.id))
    class Meta:
        model = Product
        fields = '__all__'
        #slug = 'product_name'
        exclude=['slug','prodavac']
    def __init__(self, *args, **kwargs):
        super(dodajProizvodForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    
        
    