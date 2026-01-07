from typing import Any
from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView
from .models import Category, Product
from dashboard.models import Setting


def index(request):
    setting = Setting.objects.first()
    if setting:
        categories_count = setting.homepage_categories_count
        landing_image = setting.hero_image.url if setting.hero_image else ""
    else:
        categories_count = 4
        landing_image = ""
    
    top_categories = Category.objects.all()[:categories_count]
    new_products = Product.objects.order_by("updated_at")[:12]
    return render(request, 'index.html', context={
        "categories": top_categories,
        "products": new_products,
        "landing_image": landing_image
    })


class CategoriesView(ListView):
    template_name = "categories.html"
    model = Category
    context_object_name = "categories"


class ProductListView(ListView):
    model = Product
    template_name = "products.html"
    context_object_name = "products"
    paginate_by = 12

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        category = self.request.GET.get("category", "")
        data['category'] = category
        return data

    def get_queryset(self):
        category = self.request.GET.get("category", "")
        if category:
            products = Product.objects.filter(category__name__iexact=category)
        else:
            products = Product.objects.all()

        return products


class ProductView(DetailView):
    model = Product
    template_name = 'product.html'
    context_object_name = "product"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            cart = self.request.user.cart or ""
        else:
            cart = self.request.session.get('cart') or ""

        cart = set(cart.split("-"))
        cart_products = [pr.split("#")[0] for pr in cart]
        product_id = str(self.get_object().id)
        context["in_cart"] = product_id in cart_products
        return context
    
    def post(self, request, *args, **kwargs):
        operation = request.POST.get("operation", "remove")
        variant = int(request.POST.get("product_variant", 1))
        product = self.get_object()
        product_id = str(product.id)
        
        # Prevent adding out of stock products
        if operation == "add" and product.stock == 0:
            from django.contrib import messages
            messages.error(request, f"'{product.title}' is out of stock and cannot be added to cart.")
            return redirect(request.path)
        
        if request.user.is_authenticated:
            cart = request.user.cart or ""
        else:
            cart = self.request.session.get('cart') or ""

        cart = set(cart.split("-"))
        cart_products = [pr.split("#")[0] for pr in cart]
        if operation == "add":
            if product_id not in cart_products:
                    cart.add(str(product_id) + "#" + str(variant))
        elif operation == "remove":
            for pr in list(cart):
                pr_id = pr.split("#")[0]
                if product_id == pr_id:
                    cart.remove(pr)

        cart = "-".join(list(cart))
        
        if request.user.is_authenticated:
            request.user.cart = cart
            request.user.save()

        request.session['cart'] = cart
        return redirect(request.path)

def about(request):
    return render(request, 'about.html')
