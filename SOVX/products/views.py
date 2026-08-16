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

    def get_queryset(self):
        query = self.request.GET.get('query')
        product_list_id = self.request.GET.get('product_list_id')
        
        if product_list_id:
            try:
                product_list_obj = ProductList.objects.get(id=product_list_id)
                
                if product_list_obj.product_ids.exists():
                    queryset = product_list_obj.product_ids.all()
                else:
                    queryset = Product.objects.all()
                    

                direction = "-" if product_list_obj.sort_direction.lower() == "desc" else ""
                sort_field = product_list_obj.sort_by if product_list_obj.sort_by else "id"
                
                return queryset.order_by(f"{direction}{sort_field}")
                
            except ProductList.DoesNotExist:
                return Product.objects.none()

        elif query:
            return Product.objects.filter(title__istartswith=query)

        return Product.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query')
        product_list_id = self.request.GET.get('product_list_id')
        
        results = self.object_list

        if product_list_id:
            list_obj = ProductList.objects.filter(id=product_list_id).first()
            if list_obj:
                context['search_message'] = list_obj.name
                if not results.exists():
                    context['search_message'] = f"لا توجد منتجات في قائمة: {list_obj.name}"
            else:
                context['search_message'] = "لاتوجد منتجات بهذا الإسم"
        
        elif query:
            if not results.exists():
                context['search_message'] = "لاتوجد منتجات بهذا الإسم"
            else:
                context['search_message'] = f"عرض نتائج البحث عن: {query}"
        
        return context
    
class ProductView(DetailView):
    model = Product
    template_name = "product.html"
    context_object_name = "product"
