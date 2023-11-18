from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, UpdateView

from grafita.models import Device, DevicesGroup
from grafita.views.mixins import AuthenticatedUserMixin


class DeviceGroupForm(forms.ModelForm):
    admin = forms.HiddenInput()


    class Meta:
        model = DevicesGroup
        fields = ['name', 'description', 'devices']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'devices': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['devices'].queryset = Device.objects.all()


class DeviceGroupListCreateView(AuthenticatedUserMixin, View):
    template_name = 'device_groups.html'

    def get(self, request, *args, **kwargs):
        groups = DevicesGroup.objects.all()
        form = DeviceGroupForm()
        return render(request, self.template_name, {'groups': groups, 'form': form})

    def post(self, request, *args, **kwargs):
        form = DeviceGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            return HttpResponseRedirect("/device_groups")
        return render(request, self.template_name, {'form': form})


class CreateDeviceGroupView(AuthenticatedUserMixin, CreateView):
    model = DevicesGroup
    form_class = DeviceGroupForm
    template_name = 'create_device_group.html'
    success_url = reverse_lazy('device_groups')

    def form_valid(self, form):
        form.instance.admin = self.request.user
        response = super().form_valid(form)
        return response


class UpdateDeviceGroupView(AuthenticatedUserMixin, UpdateView):
    model = DevicesGroup
    form_class = DeviceGroupForm
    template_name = 'update_device_group.html'
    success_url = reverse_lazy('device_groups')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.get_object()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


class DeviceGroupDetailView(AuthenticatedUserMixin, View):
    template_name = 'device_group_detail.html'

    def get(self, request, pk, *args, **kwargs):
        group = get_object_or_404(DevicesGroup, pk=pk)
        return render(request, self.template_name, {
            "group": group,
            "can_share": self.request.user == group.admin,
            "users": User.objects.all(),
        })


class DeleteDeviceGroupView(AuthenticatedUserMixin, View):
    template_name = 'delete_device_group.html'
    success_url = reverse_lazy('device_groups')

    def get(self, request, pk, *args, **kwargs):
        group = get_object_or_404(DevicesGroup, pk=pk)
        return render(request, self.template_name, {'group': group})

    def post(self, request, pk, *args, **kwargs):
        group = get_object_or_404(DevicesGroup, pk=pk)
        group.delete()
        return HttpResponseRedirect("/device_groups")


@require_POST
@login_required(login_url='/login')
def share_group(request, pk):
    group = get_object_or_404(DevicesGroup, pk=pk)
    user = get_object_or_404(User, pk=request.POST['recipient'])
    group.shared_with.add(user)
    return HttpResponseRedirect("/device_groups")
