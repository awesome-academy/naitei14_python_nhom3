from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect, render
from myapp.models import Product
from .cart import Cart

class CartDetailView(TemplateView):
    template_name = 'cart/detail.html'

    def get_context_data(self, **kwargs):
        cart = Cart(self.request)
        context = super().get_context_data(**kwargs)
        context['cart'] = cart
        return context

class CartAddView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        qty = int(request.POST.get('quantity', 1))
        cart = Cart(request)
        cart.add(product=product, quantity=qty)
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

        # Lấy quantity mới từ form
        try:
            new_quantity = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            return redirect("cart:detail")

        # Nếu <= 0 thì xóa khỏi giỏ
        if new_quantity <= 0:
            cart.remove(product)
        else:
            # override_quantity=True => set số lượng đúng bằng new_quantity
            cart.add(product=product, quantity=new_quantity, override_quantity=True)

        return redirect("cart:detail")
