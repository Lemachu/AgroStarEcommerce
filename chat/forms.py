from django import forms
from .models import ChatModel
from store.models import Product, ProductGallery
from category.models import Category
from accounts.models import Account
from requests import request

class PorukaForm(forms.ModelForm):
    class Meta:
        model = ChatModel
        fields = ['message']