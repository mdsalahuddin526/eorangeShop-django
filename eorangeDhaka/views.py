from store.models import Product
from django.shortcuts import render

def index(request):
    products = Product.objects.all().filter(is_available =True)
    context = {
        'products': products,
    }
    return render (request,'eorange/index.html', context)

def cart(request):
    return render (request,'eorange/cart.html')


