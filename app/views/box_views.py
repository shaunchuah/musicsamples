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

from app.filters import BasicScienceBoxFilter, ExperimentFilter
from app.forms import BasicScienceBoxForm, ExperimentForm
from app.models import BasicScienceBox, Experiment
from core.utils.export import export_csv
from core.utils.history import historical_changes

EXPERIMENT_PREFETCH = Prefetch(
    "experiments",
    queryset=Experiment.objects.prefetch_related("sample_types", "tissue_types"),
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
        context.setdefault("experiment_form", ExperimentForm())
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
        context.setdefault("experiment_form", ExperimentForm())
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
                | Q(location__icontains=query_string)
                | Q(comments__icontains=query_string)
                | Q(experiments__basic_science_group__icontains=query_string)
                | Q(experiments__name__icontains=query_string)
                | Q(experiments__sample_types__name__icontains=query_string)
                | Q(experiments__tissue_types__name__icontains=query_string)
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
                    | Q(location__icontains=query_string)
                    | Q(comments__icontains=query_string)
                    | Q(experiments__basic_science_group__icontains=query_string)
                    | Q(experiments__name__icontains=query_string)
                    | Q(experiments__sample_types__name__icontains=query_string)
                    | Q(experiments__tissue_types__name__icontains=query_string)
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
                | Q(location__icontains=query_string)
                | Q(comments__icontains=query_string)
                | Q(experiments__basic_science_group__icontains=query_string)
                | Q(experiments__name__icontains=query_string)
                | Q(experiments__sample_types__name__icontains=query_string)
                | Q(experiments__tissue_types__name__icontains=query_string)
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
                    | Q(location__icontains=query_string)
                    | Q(comments__icontains=query_string)
                    | Q(experiments__basic_science_group__icontains=query_string)
                    | Q(experiments__name__icontains=query_string)
                    | Q(experiments__sample_types__name__icontains=query_string)
                    | Q(experiments__tissue_types__name__icontains=query_string)
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


def serialize_experiment(experiment: Experiment) -> dict:
    """Serialize an Experiment for JSON responses."""

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
        for sample_type in experiment.sample_types.all()
    ]
    tissue_types = [
        {
            "id": tissue_type.pk,
            "name": tissue_type.name,
            "label": tissue_type.label,
            "display": tissue_type.label or tissue_type.name,
        }
        for tissue_type in experiment.tissue_types.all()
    ]
    boxes = [
        {
            "id": box.pk,
            "box_id": box.box_id,
            "display": str(box),
        }
        for box in experiment.boxes.all()  # type: ignore
    ]
    return {
        "id": experiment.pk,
        "basic_science_group": experiment.basic_science_group,
        "basic_science_group_display": experiment.get_basic_science_group_display(),  # type: ignore
        "name": experiment.name,
        "description": experiment.description,
        "date": experiment.date.isoformat() if experiment.date else None,
        "date_display": experiment.date.strftime("%d %b %Y") if experiment.date else None,
        "sample_types": sample_types,
        "tissue_types": tissue_types,
        "sample_type_ids": [sample_type["id"] for sample_type in sample_types],
        "tissue_type_ids": [tissue_type["id"] for tissue_type in tissue_types],
        "boxes": boxes,
        "display": f"{experiment.get_basic_science_group_display()} - {experiment.name}",  # type: ignore
        "created": experiment.created.isoformat() if experiment.created else None,
        "created_by": experiment.created_by.email if experiment.created_by else None,
        "created_display": format_timestamp(experiment.created, experiment.created_by),
        "last_modified": experiment.last_modified.isoformat() if experiment.last_modified else None,
        "last_modified_by": experiment.last_modified_by.email if experiment.last_modified_by else None,
        "last_modified_display": format_timestamp(experiment.last_modified, experiment.last_modified_by),
    }


@login_required
@permission_required("app.view_basicsciencebox", raise_exception=True)
@require_http_methods(["POST"])
def create_experiment(request):
    """AJAX view to create a new Experiment."""
    form = ExperimentForm(request.POST)

    if form.is_valid():
        experiment = form.save(commit=False)
        experiment.created_by = request.user
        experiment.last_modified_by = request.user
        experiment.save()
        form.save_m2m()
        experiment = (
            Experiment.objects.prefetch_related("sample_types", "tissue_types", "boxes")
            .select_related("created_by", "last_modified_by")
            .get(pk=experiment.pk)
        )
        return JsonResponse({"success": True, "experiment": serialize_experiment(experiment)})
    return JsonResponse({"success": False, "errors": form.errors}, status=400)


class ExperimentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Experiment
    template_name = "boxes/experiment_list.html"
    context_object_name = "experiments"
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
        context["experiment_count"] = self.get_queryset().count()
        return context


class ExperimentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Experiment
    form_class = ExperimentForm
    template_name = "boxes/experiment_form.html"
    success_url = reverse_lazy("boxes:experiment_list")
    permission_required = "app.add_basicsciencebox"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.last_modified_by = self.request.user
        messages.success(self.request, "Experiment registered successfully.")
        return super().form_valid(form)


class ExperimentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Experiment
    template_name = "boxes/experiment_detail.html"
    context_object_name = "experiment"
    permission_required = "app.view_basicsciencebox"

    def get_queryset(self):
        return super().get_queryset().select_related("created_by", "last_modified_by").prefetch_related("boxes")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        experiment = self.get_object()
        experiment_history = experiment.history.filter(id=experiment.pk)  # type: ignore
        changes = historical_changes(experiment_history)
        first_change = experiment_history.first()
        context.update(
            {
                "changes": changes,
                "first": first_change,
            }
        )
        return context


class ExperimentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Experiment
    form_class = ExperimentForm
    template_name = "boxes/experiment_form.html"
    success_url = reverse_lazy("boxes:experiment_list")
    permission_required = "app.change_basicsciencebox"

    def form_valid(self, form):
        form.instance.last_modified_by = self.request.user
        messages.success(self.request, "Experiment updated successfully.")
        return super().form_valid(form)


class ExperimentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Experiment
    template_name = "boxes/experiment_confirm_delete.html"
    success_url = reverse_lazy("boxes:experiment_list")
    permission_required = "app.delete_basicsciencebox"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.is_deleted = True  # type: ignore
        self.object.last_modified_by = self.request.user  # type: ignore
        self.object.save()
        messages.success(self.request, "Experiment deleted successfully.")
        return HttpResponseRedirect(success_url)


class ExperimentRestoreView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Experiment
    template_name = "boxes/experiment_confirm_restore.html"
    success_url = reverse_lazy("boxes:experiment_list")
    permission_required = "app.delete_basicsciencebox"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.is_deleted = False  # type: ignore
        self.object.last_modified_by = self.request.user  # type: ignore
        self.object.save()
        messages.success(self.request, "Experiment restored successfully.")
        return HttpResponseRedirect(success_url)


@login_required(login_url="/login/")
@permission_required("app.view_basicsciencebox", raise_exception=True)
def experiment_search(request):
    query_string = ""
    if ("q" in request.GET) and request.GET["q"].strip():
        query_string = request.GET.get("q")

        queryset = (
            Experiment.objects.filter(Q(name__icontains=query_string) | Q(description__icontains=query_string))
            .filter(is_deleted=False)
            .prefetch_related("boxes", "sample_types", "tissue_types")
            .select_related("created_by", "last_modified_by")
            .distinct()
        )

        experiments = queryset
        experiment_count = experiments.count()
        context = {
            "query_string": query_string,
            "experiments": experiments,
            "experiment_count": experiment_count,
        }
        return render(request, "boxes/experiment_list.html", context)
    else:
        context = {
            "query_string": "Null",
            "experiment_count": 0,
            "experiments": Experiment.objects.none(),
        }
        return render(request, "boxes/experiment_list.html", context)


@login_required(login_url="/login/")
@permission_required("app.view_basicsciencebox", raise_exception=True)
def export_experiments_csv(request):
    """
    Exports boxes to CSV based on search query or all boxes if no query.
    """
    query_string = ""
    if ("q" in request.GET) and request.GET["q"].strip():
        query_string = request.GET.get("q")
        queryset = (
            Experiment.objects.filter(Q(name__icontains=query_string) | Q(description__icontains=query_string))
            .filter(is_deleted=False)
            .prefetch_related("boxes", "sample_types", "tissue_types")
            .select_related("created_by", "last_modified_by")
            .distinct()
        )
    else:
        queryset = (
            Experiment.objects.exclude(is_deleted=True)
            .prefetch_related("boxes", "sample_types", "tissue_types")
            .select_related("created_by", "last_modified_by")
        )

    return export_csv(queryset, file_prefix="gtrac", file_name="experiments")


@login_required(login_url="/login/")
@permission_required("app.view_basicsciencebox", raise_exception=True)
def experiment_filter(request):
    queryset = (
        Experiment.objects.all()
        .prefetch_related("boxes", "sample_types", "tissue_types")
        .select_related("created_by", "last_modified_by")
    )
    experiment_filter = ExperimentFilter(request.GET, queryset=queryset)
    experiments = experiment_filter.qs
    experiment_count = experiments.count()

    # Pagination
    page = request.GET.get("page", 1)
    paginator = Paginator(experiments, 25)  # Using same pagination size as BasicScienceBoxListView
    try:
        experiments = paginator.page(page)
    except PageNotAnInteger:
        experiments = paginator.page(1)
    except EmptyPage:
        experiments = paginator.page(paginator.num_pages)

    # Allows paginator to reconstruct the initial query string
    parameter_string = ""
    for i in request.GET:
        if i != "page":
            val = request.GET.get(i)
            parameter_string += f"&{i}={val}"

    context = {
        "experiments": experiments,
        "page_obj": experiments,
        "experiment_count": experiment_count,
        "experiment_filter": experiment_filter,
        "parameter_string": parameter_string,
    }
    return render(request, "boxes/experiment_filter.html", context)


@login_required(login_url="/login/")
@permission_required("app.view_basicsciencebox", raise_exception=True)
def experiment_filter_export_csv(request):
    queryset = (
        Experiment.objects.all()
        .prefetch_related("boxes", "sample_types", "tissue_types")
        .select_related("created_by", "last_modified_by")
    )
    experiment_filter = ExperimentFilter(request.GET, queryset=queryset)
    experiments = experiment_filter.qs
    return export_csv(experiments, file_prefix="gtrac", file_name="filtered_experiments")
