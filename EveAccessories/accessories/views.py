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
        cart = self.request.session.get('cart') or ""
        cart = set(cart.split("-"))
        context["cart"] = cart
        return context
    
    def post(self, request, *args, **kwargs):
        operation = request.POST.get("operation", "remove")
        product_id = str(self.get_object().id)
        cart = request.session.get('cart') or ""
        cart = set(cart.split("-"))

        if operation == "add":
            if product_id not in cart:
                    cart.add(str(product_id))
        elif operation == "remove":
            if product_id in cart:
                cart.remove(str(product_id))

        request.session['cart'] = "-".join(list(cart))
        return redirect(request.path)
    
def cart(request):
    cart = request.session.get('cart') or ""
    cart = cart.strip("-")
    product_ids = list(map(int, cart.split("-")))
    products = Product.objects.filter(id__in=product_ids)
    return render(request, 'cart.html', context={"products": products})


def about(request):
    return render(request, 'about.html')
