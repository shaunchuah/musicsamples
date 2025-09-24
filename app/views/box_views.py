from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Prefetch, Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from app.filters import BasicScienceBoxFilter
from app.forms import BasicScienceBoxForm, ExperimentalIDForm
from app.models import BasicScienceBox, ExperimentalID
from app.utils import export_csv, historical_changes

EXPERIMENT_PREFETCH = Prefetch(
    "experimental_ids",
    queryset=ExperimentalID.objects.prefetch_related("sample_types", "tissue_types"),
)


class BasicScienceBoxDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = BasicScienceBox
    template_name = "boxes/box_detail.html"
    context_object_name = "box"
    permission_required = "app.view_basicsciencebox"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("created_by", "last_modified_by")
            .prefetch_related(EXPERIMENT_PREFETCH)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        box = self.get_object()
        box_history = box.history.filter(id=box.pk)  # type: ignore
        changes = historical_changes(box_history)
        first_change = box_history.first()
        context.update(
            {
                "changes": changes,
                "first": first_change,
            }
        )
        return context


class BasicScienceBoxListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = BasicScienceBox
    template_name = "boxes/box_list.html"
    context_object_name = "boxes"
    paginate_by = 20
    permission_required = "app.view_basicsciencebox"

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .exclude(is_used=True)
            .prefetch_related(EXPERIMENT_PREFETCH)
            .select_related("created_by", "last_modified_by")
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["box_count"] = self.get_queryset().count()
        return context


class BasicScienceBoxCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = BasicScienceBox
    form_class = BasicScienceBoxForm
    template_name = "boxes/box_form.html"
    success_url = reverse_lazy("boxes:list")
    permission_required = "app.add_basicsciencebox"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("experimental_form", ExperimentalIDForm())
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.last_modified_by = self.request.user
        messages.success(self.request, "Box registered successfully.")
        return super().form_valid(form)


class BasicScienceBoxUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = BasicScienceBox
    form_class = BasicScienceBoxForm
    template_name = "boxes/box_form.html"
    success_url = reverse_lazy("boxes:list")
    permission_required = "app.change_basicsciencebox"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("experimental_form", ExperimentalIDForm())
        return context

    def form_valid(self, form):
        form.instance.last_modified_by = self.request.user
        messages.success(self.request, "Box updated successfully.")
        return super().form_valid(form)


class BasicScienceBoxDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = BasicScienceBox
    template_name = "boxes/box_confirm_delete.html"
    success_url = reverse_lazy("boxes:list")
    permission_required = "app.delete_basicsciencebox"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.is_used = True  # type: ignore
        self.object.last_modified_by = self.request.user  # type: ignore
        self.object.save()
        messages.success(self.request, "Box deleted successfully.")
        return HttpResponseRedirect(success_url)


@login_required(login_url="/login/")
@permission_required("app.view_basicsciencebox", raise_exception=True)
def box_search(request):
    query_string = ""
    if ("q" in request.GET) and request.GET["q"].strip():
        query_string = request.GET.get("q")

        queryset = (
            BasicScienceBox.objects.filter(
                Q(box_id__icontains=query_string)
                | Q(basic_science_group__icontains=query_string)
                | Q(location__icontains=query_string)
                | Q(comments__icontains=query_string)
                | Q(experimental_ids__name__icontains=query_string)
                | Q(experimental_ids__sample_types__name__icontains=query_string)
                | Q(experimental_ids__tissue_types__name__icontains=query_string)
            )
            .filter(is_used=False)
            .prefetch_related(EXPERIMENT_PREFETCH)
            .select_related("created_by", "last_modified_by")
            .distinct()
        )

        if ("include_used_boxes" in request.GET) and request.GET["include_used_boxes"].strip():
            queryset = (
                BasicScienceBox.objects.filter(
                    Q(box_id__icontains=query_string)
                    | Q(basic_science_group__icontains=query_string)
                    | Q(location__icontains=query_string)
                    | Q(comments__icontains=query_string)
                    | Q(experimental_ids__name__icontains=query_string)
                    | Q(experimental_ids__sample_types__name__icontains=query_string)
                    | Q(experimental_ids__tissue_types__name__icontains=query_string)
                )
                .prefetch_related(EXPERIMENT_PREFETCH)
                .select_related("created_by", "last_modified_by")
                .distinct()
            )

        box_list = queryset
        box_count = box_list.count()
        context = {
            "query_string": query_string,
            "boxes": box_list,
            "box_count": box_count,
        }
        return render(request, "boxes/box_list.html", context)
    else:
        context = {"query_string": "Null", "box_count": 0, "boxes": BasicScienceBox.objects.none()}
        return render(request, "boxes/box_list.html", context)


@login_required(login_url="/login/")
@permission_required("app.view_basicsciencebox", raise_exception=True)
def export_boxes_csv(request):
    """
    Exports boxes to CSV based on search query or all boxes if no query.
    """
    query_string = ""
    if ("q" in request.GET) and request.GET["q"].strip():
        query_string = request.GET.get("q")
        queryset = (
            BasicScienceBox.objects.filter(
                Q(box_id__icontains=query_string)
                | Q(basic_science_group__icontains=query_string)
                | Q(location__icontains=query_string)
                | Q(comments__icontains=query_string)
                | Q(experimental_ids__name__icontains=query_string)
                | Q(experimental_ids__sample_types__name__icontains=query_string)
                | Q(experimental_ids__tissue_types__name__icontains=query_string)
            )
            .filter(is_used=False)
            .prefetch_related(EXPERIMENT_PREFETCH)
            .select_related("created_by", "last_modified_by")
            .distinct()
        )

        if ("include_used_boxes" in request.GET) and request.GET["include_used_boxes"].strip():
            queryset = (
                BasicScienceBox.objects.filter(
                    Q(box_id__icontains=query_string)
                    | Q(basic_science_group__icontains=query_string)
                    | Q(location__icontains=query_string)
                    | Q(comments__icontains=query_string)
                    | Q(experimental_ids__name__icontains=query_string)
                    | Q(experimental_ids__sample_types__name__icontains=query_string)
                    | Q(experimental_ids__tissue_types__name__icontains=query_string)
                )
                .prefetch_related(EXPERIMENT_PREFETCH)
                .select_related("created_by", "last_modified_by")
                .distinct()
            )
    else:
        queryset = (
            BasicScienceBox.objects.exclude(is_used=True)
            .prefetch_related(EXPERIMENT_PREFETCH)
            .select_related("created_by", "last_modified_by")
        )

    return export_csv(queryset, file_prefix="gtrac", file_name="basic_science_boxes")


@login_required(login_url="/login/")
@permission_required("app.view_basicsciencebox", raise_exception=True)
def box_filter(request):
    queryset = (
        BasicScienceBox.objects.all()
        .prefetch_related(EXPERIMENT_PREFETCH)
        .select_related("created_by", "last_modified_by")
    )
    box_filter = BasicScienceBoxFilter(request.GET, queryset=queryset)
    box_list = box_filter.qs
    box_count = box_list.count()

    # Pagination
    page = request.GET.get("page", 1)
    paginator = Paginator(box_list, 25)  # Using same pagination size as BasicScienceBoxListView
    try:
        boxes = paginator.page(page)
    except PageNotAnInteger:
        boxes = paginator.page(1)
    except EmptyPage:
        boxes = paginator.page(paginator.num_pages)

    # Allows paginator to reconstruct the initial query string
    parameter_string = ""
    for i in request.GET:
        if i != "page":
            val = request.GET.get(i)
            parameter_string += f"&{i}={val}"

    context = {
        "box_list": boxes,
        "page_obj": boxes,
        "box_count": box_count,
        "box_filter": box_filter,
        "parameter_string": parameter_string,
    }
    return render(request, "boxes/box_filter.html", context)


@login_required(login_url="/login/")
@permission_required("app.view_basicsciencebox", raise_exception=True)
def box_filter_export_csv(request):
    queryset = (
        BasicScienceBox.objects.all()
        .prefetch_related(EXPERIMENT_PREFETCH)
        .select_related("created_by", "last_modified_by")
    )
    box_filter = BasicScienceBoxFilter(request.GET, queryset=queryset)
    box_list = box_filter.qs
    return export_csv(box_list, file_prefix="gtrac", file_name="filtered_basic_science_boxes")


def serialize_experimental_id(experimental_id: ExperimentalID) -> dict:
    """Serialize an ExperimentalID for JSON responses."""

    def format_timestamp(value, user):
        if not value:
            return None
        formatted = value.strftime("%d %b %Y %H:%M")
        if user:
            return f"{formatted} · {user.email}"
        return formatted

    sample_types = [
        {
            "id": sample_type.pk,
            "name": sample_type.name,
            "label": sample_type.label,
            "display": sample_type.label or sample_type.name,
        }
        for sample_type in experimental_id.sample_types.all()
    ]
    tissue_types = [
        {
            "id": tissue_type.pk,
            "name": tissue_type.name,
            "label": tissue_type.label,
            "display": tissue_type.label or tissue_type.name,
        }
        for tissue_type in experimental_id.tissue_types.all()
    ]
    boxes = [
        {
            "id": box.pk,
            "box_id": box.box_id,
            "display": str(box),
        }
        for box in experimental_id.boxes.all()  # type: ignore
    ]
    return {
        "id": experimental_id.pk,
        "name": experimental_id.name,
        "description": experimental_id.description,
        "date": experimental_id.date.isoformat() if experimental_id.date else None,
        "date_display": experimental_id.date.strftime("%d %b %Y") if experimental_id.date else None,
        "sample_types": sample_types,
        "tissue_types": tissue_types,
        "sample_type_ids": [sample_type["id"] for sample_type in sample_types],
        "tissue_type_ids": [tissue_type["id"] for tissue_type in tissue_types],
        "boxes": boxes,
        "created": experimental_id.created.isoformat() if experimental_id.created else None,
        "created_by": experimental_id.created_by.email if experimental_id.created_by else None,
        "created_display": format_timestamp(experimental_id.created, experimental_id.created_by),
        "last_modified": experimental_id.last_modified.isoformat() if experimental_id.last_modified else None,
        "last_modified_by": experimental_id.last_modified_by.email if experimental_id.last_modified_by else None,
        "last_modified_display": format_timestamp(experimental_id.last_modified, experimental_id.last_modified_by),
    }


@login_required
@permission_required("app.view_basicsciencebox", raise_exception=True)
@require_http_methods(["POST"])
def create_experimental_id(request):
    """AJAX view to create a new ExperimentalID."""
    form = ExperimentalIDForm(request.POST)

    if form.is_valid():
        experimental_id = form.save(commit=False)
        experimental_id.created_by = request.user
        experimental_id.last_modified_by = request.user
        experimental_id.save()
        form.save_m2m()
        experimental_id = (
            ExperimentalID.objects.prefetch_related("sample_types", "tissue_types", "boxes")
            .select_related("created_by", "last_modified_by")
            .get(pk=experimental_id.pk)
        )
        return JsonResponse({"success": True, "experimental_id": serialize_experimental_id(experimental_id)})
    return JsonResponse({"success": False, "errors": form.errors}, status=400)


class ExperimentalIdListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = ExperimentalID
    template_name = "boxes/experimental_id_list.html"
    context_object_name = "experimental_ids"
    paginate_by = 20
    permission_required = "app.view_basicsciencebox"

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .exclude(is_deleted=True)
            .prefetch_related("sample_types", "tissue_types", "boxes")
            .select_related("created_by", "last_modified_by")
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["experimental_id_count"] = self.get_queryset().count()
        return context


class ExperimentalIdDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = ExperimentalID
    template_name = "boxes/experimental_id_detail.html"
    context_object_name = "experimental_id"
    permission_required = "app.view_basicsciencebox"

    def get_queryset(self):
        return super().get_queryset().select_related("created_by", "last_modified_by").prefetch_related("boxes")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        experimental_id = self.get_object()
        experimental_id_history = experimental_id.history.filter(id=experimental_id.pk)  # type: ignore
        changes = historical_changes(experimental_id_history)
        first_change = experimental_id_history.first()
        context.update(
            {
                "changes": changes,
                "first": first_change,
            }
        )
        return context
