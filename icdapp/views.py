from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .filters import ICDSearchFilter
from .forms import ICDForm
from .models import ICDModel

PAGE_TITLE = "ICD Codes"


def index_view(request):
    icd = ICDModel.objects.all()
    search_filter = ICDSearchFilter(request.GET, queryset=icd)
    search_term = request.GET.get("category_title", "")
    paginator = Paginator(search_filter.qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    # The current query string WITHOUT "page", so that the pagination links keep
    # the search filters (e.g. "category_title=chol&").
    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    context = {
        "title": PAGE_TITLE,
        "search_filter": search_filter,
        "page_obj": page_obj,
        "search_term": search_term,
        "querystring": (querystring + "&") if querystring else "",
        # Delete buttons are for staff only.
        "can_edit": request.user.is_staff,
    }
    return render(request, "index.html", context)


def about_view(request):
    context = {"title": PAGE_TITLE}
    return render(request, "about.html", context)


@require_http_methods(["GET", "POST"])
def add_view(request):
    """
    Form for adding a new ICD record.

    Open to everyone while settings.ICD_PUBLIC_ADD is true (the default);
    otherwise only logged-in staff may use it.
    """
    user = request.user
    if not (settings.ICD_PUBLIC_ADD or (user.is_active and user.is_staff)):
        return redirect_to_login(request.get_full_path(), resolve_url(settings.LOGIN_URL))

    if request.method == "POST":
        form = ICDForm(request.POST)
        if form.is_valid():
            icd = form.save()
            messages.success(request, f"ICD code {icd.full_code} was added.")
            # Show the new record straight away: search results for its category code.
            url = reverse("index")
            if icd.category_code:
                url += "?" + urlencode({"category_code": icd.category_code})
            return redirect(url)
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
