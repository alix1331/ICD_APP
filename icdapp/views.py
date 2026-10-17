from django.shortcuts import render
from django.core.paginator import Paginator
from .models import ICDModel
from .filters import ICDSearchFilter


# Create your views here.
def index_view(request):
    icd = ICDModel.objects.all()
    search_filter = ICDSearchFilter(request.GET, queryset=icd)
    search_term = request.GET.get("category_title","")
    icd_list = search_filter.qs
    paginator = Paginator(icd_list, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"title": "Hello Backend Developers", "search_filter": search_filter, "page_obj": page_obj,
               "search_term":search_term}
    return render(request, "index.html", context)

def about_view(request):
    context = {"title": "Hello Backend Developers",}
    return render(request, "about.html", context)