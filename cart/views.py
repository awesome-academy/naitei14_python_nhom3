from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from myapp.models import Product
from .cart import Cart
from django.contrib.auth.mixins import LoginRequiredMixin


class CartDetailView(TemplateView):
    template_name = 'cart/detail.html'

    def get_context_data(self, **kwargs):
        cart = Cart(self.request)
        context = super().get_context_data(**kwargs)
        context['cart'] = cart
        return context

class CartAddView(View):
    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        
        if product.stock_quantity <= 0:
            messages.error(request, f"Rất tiếc, sản phẩm '{product.name}' đã hết hàng!")
            return redirect(request.META.get('HTTP_REFERER', 'products:list'))

        try:
            qty = int(request.POST.get('quantity', 1))
        except (TypeError, ValueError):
            qty = 1
        
        if qty < 1:
            qty = 1
            
        if qty > product.stock_quantity:
            messages.warning(request, f"Chỉ còn {product.stock_quantity} sản phẩm '{product.name}' trong kho.")
            return redirect(request.META.get('HTTP_REFERER', 'products:list'))

        cart.add(product=product, quantity=qty)
        
        messages.success(request, f'Đã thêm {qty} x "{product.name}" vào giỏ hàng.')
        
        return redirect('cart:detail')

class CartRemoveView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        cart = Cart(request)
        cart.remove(product)
        return redirect('cart:detail')

class CartUpdateView(View):
    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)

        try:
            new_quantity = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            return redirect("cart:detail")

        # Nếu <= 0 thì xóa khỏi giỏ
        if new_quantity <= 0:
            cart.remove(product)
            return redirect("cart:detail")
        
        #Nếu > tồn kho thì không hợp lệ
        if new_quantity > product.stock_quantity:
            return redirect("cart:detail")
        
        # override_quantity=True => set số lượng đúng bằng new_quantity
        cart.add(product=product, quantity=new_quantity, override_quantity=True)
        return redirect("cart:detail")