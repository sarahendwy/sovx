from typing import Any
from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView
from .models import Product
from dashboard.models import ProductList

from dashboard.models import Section, SectionType, SellWithUsCard


def index(request):
    sections = Section.objects.all()
    context = {"sections": sections}

    if sections.filter(type=SectionType.SELL_WITH_US).exists():
        context["sell_with_us_cards"] = SellWithUsCard.objects.filter(disabled=False)

    return render(request, "index.html", context=context)

class ProductListView(ListView):
    model = Product
    template_name = "products.html"
    context_object_name = "products"

    def dispatch(self, request, *args, **kwargs):
        query = request.GET.get('q')

        if 'q' in request.GET and not query.strip():
            return redirect('index')  
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = Product.objects.all()
        query = self.request.GET.get('q')

        if query:
            if query.isdigit():
                product_list_obj = ProductList.objects.filter(id=query).first()

                if product_list_obj:
                    if product_list_obj.product_ids.exists():
                        queryset = product_list_obj.product_ids.all()
                    else:
                        queryset = Product.objects.all()
                    
                    direction = "-" if product_list_obj.sort_direction == "DESC" else ""
                    queryset = queryset.order_by(f"{direction}{product_list_obj.sort_by}")
                    
                    queryset = queryset[:product_list_obj.limit]
                else:
                    queryset = Product.objects.none()

            else:
                queryset = queryset.filter(title__icontains=query)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q')

        if query:
            if query.isdigit():
                product_list_obj = ProductList.objects.filter(id=query).first()
                
                if product_list_obj:
                    context['search_message'] = f"عرض نتائج البحث في قائمة : {product_list_obj.name}"
                else:
                    context['search_message'] = f"لا توجد قائمة تحمل الرقم التعريفي: {query}"
            else:
                context['search_message'] = f"عرض نتائج البحث عن: {query}"
        
        return context

class ProductView(DetailView):
    model = Product
    template_name = "product.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            cart = self.request.user.cart or ""
        else:
            cart = self.request.session.get("cart") or ""

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

            messages.error(
                request,
                f"'{product.title}' is out of stock and cannot be added to cart.",
            )
            return redirect(request.path)

        if request.user.is_authenticated:
            cart = request.user.cart or ""
        else:
            cart = self.request.session.get("cart") or ""

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

        request.session["cart"] = cart
        return redirect(request.path)


def about(request):
    return render(request, "about.html")
