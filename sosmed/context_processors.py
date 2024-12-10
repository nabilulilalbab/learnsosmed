from .models import Category
from django.core.cache import cache




def categories(request):
    categories = cache.get('categories')
    if not categories:
        categories = Category.objects.all()
        cache.set('categories', categories, 60 * 15)  # Cache selama 15 menit
    return {'categories': categories}