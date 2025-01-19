from typing import Any
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView
from .models import Category, Product


def index(request):
    top_categories = Category.objects.all()[:4]
    new_products = Product.objects.order_by("updated_at")[:12]
    return render(request, 'index.html', context={"categories": top_categories, "products": new_products})


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
        product_id = str(self.get_object().id)
        context["in_cart"] = product_id in cart
        return context
    
    def post(self, request, *args, **kwargs):
        operation = request.POST.get("operation", "remove")
        product_id = str(self.get_object().id)
        if request.user.is_authenticated:
            cart = request.user.cart or ""
        else:
            cart = self.request.session.get('cart') or ""

        cart = set(cart.split("-"))

        if operation == "add":
            if product_id not in cart:
                    cart.add(str(product_id))
        elif operation == "remove":
            if product_id in cart:
                cart.remove(str(product_id))

        cart = "-".join(list(cart))
        
        if request.user.is_authenticated:
            request.user.cart = cart
            request.user.save()

        request.session['cart'] = cart
        return redirect(request.path)

def about(request):
    return render(request, 'about.html')
