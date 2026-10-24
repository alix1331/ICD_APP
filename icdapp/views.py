from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .filters import ICDSearchFilter
from .forms import ICDForm
from .models import ICDModel

PAGE_TITLE = "ICD Codes"


def index_view(request):
    icd = ICDModel.objects.all()
    search_filter = ICDSearchFilter(request.GET, queryset=icd)
    search_term = request.GET.get("category_title", "")
    icd_list = search_filter.qs
    paginator = Paginator(icd_list, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "title": PAGE_TITLE,
        "search_filter": search_filter,
        "page_obj": page_obj,
        "search_term": search_term,
        # Templates can use this to show the "Add" / "Delete" controls.
        "can_edit": request.user.is_staff,
    }
    return render(request, "index.html", context)


def about_view(request):
    context = {"title": PAGE_TITLE}
    return render(request, "about.html", context)


@staff_member_required
@require_http_methods(["GET", "POST"])
def add_view(request):
    """Staff only: form for adding a new ICD record."""
    if request.method == "POST":
        form = ICDForm(request.POST)
        if form.is_valid():
            icd = form.save()
            messages.success(request, f"ICD code {icd.full_code} was added.")
            return redirect("index")
    else:
        form = ICDForm()
    return render(request, "icd_form.html", {"title": "Add ICD code", "form": form})


@staff_member_required
@require_http_methods(["GET", "POST"])
def delete_view(request, pk):
    """Staff only: confirmation page (GET) and the actual delete (POST)."""
    icd = get_object_or_404(ICDModel, pk=pk)
    if request.method == "POST":
        code = icd.full_code
        icd.delete()
        messages.success(request, f"ICD code {code} was deleted.")
        return redirect("index")
    return render(request, "icd_confirm_delete.html", {"title": "Delete ICD code", "icd": icd})
