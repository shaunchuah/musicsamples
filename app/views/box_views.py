from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from app.filters import BasicScienceBoxFilter
from app.forms import BasicScienceBoxForm
from app.models import BasicScienceBox


class BasicScienceBoxListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = BasicScienceBox
    template_name = "boxes/box_list.html"
    context_object_name = "boxes"
    paginate_by = 25
    permission_required = "app.view_basicsciencebox"

    def get_queryset(self):
        queryset = super().get_queryset().exclude(is_used=True)
        self.filterset = BasicScienceBoxFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        return context


class BasicScienceBoxCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = BasicScienceBox
    form_class = BasicScienceBoxForm
    template_name = "boxes/box_form.html"
    success_url = reverse_lazy("boxes:list")
    permission_required = "app.add_basicsciencebox"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.last_modified_by = self.request.user
        return super().form_valid(form)


class BasicScienceBoxUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = BasicScienceBox
    form_class = BasicScienceBoxForm
    template_name = "boxes/box_form.html"
    success_url = reverse_lazy("boxes:list")
    permission_required = "app.change_basicsciencebox"

    def form_valid(self, form):
        form.instance.last_modified_by = self.request.user
        return super().form_valid(form)


class BasicScienceBoxDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = BasicScienceBox
    template_name = "boxes/box_confirm_delete.html"
    success_url = reverse_lazy("boxes:list")
    permission_required = "app.delete_basicsciencebox"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.is_used = True  # type: ignore
        self.object.last_modified_by = self.request.user  # type: ignore
        self.object.save()
        return HttpResponseRedirect(success_url)


@login_required(login_url="/login/")
def box_search(request):
    query_string = ""
    if ("q" in request.GET) and request.GET["q"].strip():
        query_string = request.GET.get("q")

        queryset = BasicScienceBox.objects.filter(
            Q(box_id__icontains=query_string)
            | Q(box_type__icontains=query_string)
            | Q(basic_science_group__icontains=query_string)
            | Q(location__icontains=query_string)
            | Q(species__icontains=query_string)
        ).filter(is_used=False)

        if ("include_used_boxes" in request.GET) and request.GET["include_used_boxes"].strip():
            queryset = BasicScienceBox.objects.filter(
                Q(box_id__icontains=query_string)
                | Q(box_type__icontains=query_string)
                | Q(basic_science_group__icontains=query_string)
                | Q(location__icontains=query_string)
                | Q(species__icontains=query_string)
            )

        box_list = queryset
        box_count = box_list.count()
        return render(
            request,
            "boxes/box_list.html",
            {
                "query_string": query_string,
                "boxes": box_list,
                "box_count": box_count,
            },
        )
    else:
        return render(request, "boxes/box_list.html", {"query_string": "Null", "box_count": 0})
