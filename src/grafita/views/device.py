from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from grafita.models import Device, DevicesGroup
from grafita.views.mixins import AuthenticatedUserMixin


class DeviceForm(forms.ModelForm):
    template_name = "snippets/standard_form.html"

    class Meta:
        model = Device
        fields = ['name', 'model', 'description', 'location', 'device_group', 'device_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'device_type': forms.TextInput(attrs={'class': 'form-control'}),
            'device_group': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, request, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['device_group'].queryset = DevicesGroup.objects.filter(admin=request.user)


class DeviceList(AuthenticatedUserMixin, ListView):
    model = Device
    paginate_by = 100
    ordering = ['-id']
    template_name = 'devices.html'

    def get_queryset(self):
        return Device.objects.filter(Q(created_by=self.request.user) | Q(can_view=self.request.user))


class DeviceDetail(AuthenticatedUserMixin, DetailView):
    model = Device
    template_name = 'device_detail.html'

    def test_func(self):
        return super().test_func() and (
                self.get_object().created_by == self.request.user
                or
                self.get_object().can_view.filter(pk=self.request.user.pk).exists()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        context['can_share'] = self.get_object().created_by == self.request.user
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            action = request.POST.get("action")
            if action == "delete":
                return self.delete(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def delete(request, pk: int):
        if request.user.is_authenticated:
            device = get_object_or_404(Device, pk=pk)
            device.delete()
        else:
            raise PermissionDenied("User is not authenticated")
        return HttpResponseRedirect("/devices")


class DeleteDeviceView(AuthenticatedUserMixin, View):
    def post(self, request, pk):
        if request.user.is_authenticated:
            device = get_object_or_404(Device, pk=pk)
            device.delete()
            return HttpResponseRedirect("/devices")
        else:
            raise PermissionDenied("User is not authenticated")


class UpdateDeviceView(UpdateView):
    model = Device
    form_class = DeviceForm
    template_name = 'edit_device.html'
    success_url = '/devices'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        device = self.get_object()
        if form.cleaned_data['device_group'] != device.device_group:
            if device.device_group is not None:
                device.device_group.devices.remove(device)
                device.device_group.save()
            if form.cleaned_data['device_group'] is not None:
                form.cleaned_data['device_group'].devices.add(device)
                form.cleaned_data['device_group'].save()

        super().form_valid(form)

        return HttpResponseRedirect("/devices")


class CreateDeviceView(AuthenticatedUserMixin, CreateView):
    model = Device
    form_class = DeviceForm
    template_name = 'create_device.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs['form'] = None
        context = super().get_context_data(**kwargs)
        context["device_form"] = DeviceForm(request=self.request)
        return context

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            return HttpResponseForbidden()

        data = form.cleaned_data

        device = Device(
            name=data['name'],
            model=data['model'],
            description=data['description'],
            location=data['location'],
            device_group=data['device_group'],
            created_by=self.request.user,
            device_type=data['device_type'],
        )
        device.save()

        if device.device_group is not None:
            device.device_group.devices.add(device)
            device.device_group.save()

        return HttpResponseRedirect("/devices")


@login_required
@require_POST
def share_device(request, pk):
    device = get_object_or_404(Device, pk=pk)
    used_id = request.POST.get('recipient')
    if used_id is None:
        return HttpResponseForbidden()

    device.can_view.add(User.objects.get(pk=used_id))
    device.save()
    return HttpResponseRedirect("/devices")
