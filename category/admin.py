from django.contrib import admin
#from django.contrib.admin.decorators import display
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields ={'slug': ('category_name',)}
    list_display = ('category_name', 'slug')




    

