from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from myapp.models import Product
from .cart import Cart
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _

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
        
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

        # 1. Kiểm tra hết hàng
        if product.stock_quantity <= 0:
            msg = f"Rất tiếc, sản phẩm '{product.name}' đã hết hàng!"
            if is_ajax:
                return JsonResponse({'success': False, 'message': msg}, status=400)
            
            messages.error(request, msg)
            return redirect(request.META.get('HTTP_REFERER', 'products:list'))
        
        try:
            qty = int(request.POST.get('quantity', 1))
        except (TypeError, ValueError):
            qty = 1
        
        if qty < 1:
            qty = 1
            
        # 2. Kiểm tra số lượng tồn kho
        if qty > product.stock_quantity:
            msg = f"Chỉ còn {product.stock_quantity} sản phẩm '{product.name}' trong kho."
            if is_ajax:
                return JsonResponse({'success': False, 'message': msg}, status=400)
                
            messages.warning(request, msg)
            return redirect(request.META.get('HTTP_REFERER', 'products:list'))

        # 3. Thêm vào giỏ
        cart.add(product=product, quantity=qty)
        
        # === TRẢ VỀ KẾT QUẢ ===
        # msg_success = f'Đã thêm "{product.name}" vào giỏ hàng.'
        msg_success = _('Added "%(product_name)s" to cart.') % {'product_name': product.name}
        # messages.success(request, msg_success)        
        if is_ajax:
            return JsonResponse({
                'success': True, 
                'message': msg_success,
                'cart_total': len(cart) 
            })
        
        # Nếu không phải Ajax: Redirect như cũ
        messages.success(request, _(msg_success))
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