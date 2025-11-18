from django.views.generic.edit import CreateView, DeleteView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .models import Comment
from products.models import Product
from django.contrib.auth.mixins import LoginRequiredMixin

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['content']

    def form_valid(self, form):
        product_id = self.kwargs['product_id']
        product = get_object_or_404(Product, id=product_id)
        form.instance.user = self.request.user
        form.instance.product = product
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'slug': self.kwargs['slug']})

class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment

    def get_object(self, queryset=None):
        comment = super().get_object(queryset)
        if comment.user != self.request.user:
            raise PermissionError("Cannot delete others' comments")
        return comment

    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'slug': self.object.product.slug})
