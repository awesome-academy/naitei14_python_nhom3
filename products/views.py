from django.views.generic import ListView, DetailView
from django.db.models import Avg, Count, Q

from myapp.models import Product, OrderItem  
from comments.models import Comment


class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        products_queryset = Product.objects.all()
        search_query = self.request.GET.get('q', '')
        category = self.request.GET.get('category', '')
        if search_query:
            products_queryset = products_queryset.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
        # if category:
        #     products_queryset = products_queryset.filter(category__name__icontains=category)
        return products_queryset

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        # danh sách comment
        comments_qs = Comment.objects.filter(product=product).select_related('user')
        rating_aggregates = comments_qs.aggregate(
            avg_rating=Avg('rating'),
            count_rating=Count('id')
        )

        context['comments'] = comments_qs
        context['average_rating'] = rating_aggregates['avg_rating']
        context['rating_count'] = rating_aggregates['count_rating']

        # Kiểm tra user hiện tại có mua và nhận sản phẩm này (để được phép đánh giá)
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