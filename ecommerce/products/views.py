from django.views.generic import ListView, DetailView
from .models import Product, Category

class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        qs = Product.objects.all()
        q = self.request.GET.get('q', '')
        category = self.request.GET.get('category', '')
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(description__icontains=q)
        if category:
            qs = qs.filter(category__slug=category)
        return qs

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
