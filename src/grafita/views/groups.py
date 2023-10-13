from django import forms
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, ListView


class NewGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name"]


class GroupList(ListView):
    model = Group
    paginate_by = 100
    form_class = NewGroupForm
    template_name = 'admin/groups.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class()
        return context

    def post(self, request):
        form: NewGroupForm = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            group = Group.objects.create(**data)
            group.save()

        return HttpResponseRedirect("/groups")


class ConcreteGroup(DetailView):
    model = Group
    template_name = 'admin/group_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["permissions"] = Permission.objects.all()
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("user is not authenticated")
        if request.method == "POST":
            action = request.POST.get("action")
            if action == "delete":
                return self.delete(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def delete(_, pk: int):
        Group.objects.get(id=pk).delete()
        return HttpResponseRedirect("/groups")

    @staticmethod
    def add_permission(request, pk: int):
        group = Group.objects.get(id=pk)
        permission_id = request.POST.get("permission")
        permission = Permission.objects.get(id=permission_id)
        group.permissions.add(permission)
        group.save()
        return HttpResponseRedirect(f"/group/{pk}")

    @staticmethod
    def remove_permission(request, pk: int):
        group = Group.objects.get(id=pk)
        permission_id = request.POST.get("permission")
        permission = Permission.objects.get(id=permission_id)
        group.permissions.remove(permission)
        group.save()
        return HttpResponseRedirect(f"/group/{pk}")
