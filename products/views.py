from django.views.generic import ListView, DetailView
from django.db.models import Avg, Count

from myapp.models import Product, OrderItem  
from comments.models import Comment


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
            qs = qs.filter(category__name__icontains=category)
        return qs


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        # danh sách comment
        comments_qs = Comment.objects.filter(product=product).select_related('user')
        agg = comments_qs.aggregate(
            avg_rating=Avg('rating'),
            count_rating=Count('id')
        )

        context['comments'] = comments_qs
        context['average_rating'] = agg['avg_rating']
        context['rating_count'] = agg['count_rating']

        # 👇 kiểm tra user hiện tại có được comment không
        can_comment = False
        user = self.request.user
        if user.is_authenticated:
            can_comment = OrderItem.objects.filter(
                order__user=user,
                order__status='completed',
                product=product
            ).exists()

        context['can_comment'] = can_comment
        return context
