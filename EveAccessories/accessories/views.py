from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Category, Product


# Create your views here.
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


def cart(request):
    return render(request, 'cart.html')


def about(request):
    return render(request, 'about.html')
