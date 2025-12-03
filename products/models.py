# from django.db import models
# from django.utils.text import slugify

# class Category(models.Model):
#     name = models.CharField(max_length=120)
#     slug = models.SlugField(max_length=150, unique=True, blank=True)

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.name)
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.name

# class Product(models.Model):
#     name = models.CharField(max_length=255)
#     slug = models.SlugField(max_length=255, unique=True, blank=True)
#     description = models.TextField(blank=True)
#     price = models.DecimalField(max_digits=12, decimal_places=2)
#     stock = models.PositiveIntegerField(default=0)
#     category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
#     is_featured = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     image = models.ImageField(upload_to='products/', null=True, blank=True)

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             base = slugify(self.name)
#             slug = base
#             i = 1
#             while Product.objects.filter(slug=slug).exists():
#                 slug = f"{base}-{i}"
#                 i += 1
#             self.slug = slug
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.name
