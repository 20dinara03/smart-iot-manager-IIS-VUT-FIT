from django import forms
from django.core.exceptions import PermissionDenied
from grafita.models import Device, DeviceType
from django.views.generic import ListView, DetailView, CreateView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from grafita.views.types import DeviceTypeForm


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['name', 'model', 'description', 'location', 'device_type', 'device_group', 'created_by', 'value_min',
                  'value_max', 'default_kpi']
        widgets = {
            'device_type': forms.Select(attrs={'class': 'form-control'}),
            'device_group': forms.Select(attrs={'class': 'form-control'}),
            'default_kpi': forms.Select(attrs={'class': 'form-control'}),
        }


class DeviceList(ListView):
    model = Device
    paginate_by = 100
    template_name = 'devices.html'


class DeviceDetail(DetailView):
    model = Device
    template_name = 'device_detail.html'

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


class CreateDeviceView(CreateView):
    model = Device
    form_class = DeviceForm
    template_name = 'create_device.html'

    def post(self, request, *args, **kwargs):
        device_form = DeviceForm(request.POST)
        device_type_form = DeviceTypeForm(request.POST)

        if device_form.is_valid() and device_type_form.is_valid():
            data = device_form.cleaned_data
            new_device_type = device_form.cleaned_data.get('new_device_type')

            if new_device_type:
                device_type = DeviceType(
                    name=new_device_type,
                    description=device_type_form.cleaned_data['description']
                )
                device_type.save()
            else:
                device_type = data['device_type']

            device = Device(
                name=data['name'],
                model=data['model'],
                description=data['description'],
                location=data['location'],
                device_type=device_type,
                device_group=data['device_group'],
                created_by=data['created_by'],
                value_min=data['value_min'],
                value_max=data['value_max'],
                default_kpi=data['default_kpi']
            )
            device.save()

            return HttpResponseRedirect("/devices")
        return render(request, 'create_device.html',
                      {'device_form': device_form, 'device_type_form': device_type_form})

    def get(self, request, *args, **kwargs):
        device_form = DeviceForm()
        device_type_form = DeviceTypeForm()
        return render(request, 'create_device.html',
                      {'device_form': device_form, 'device_type_form': device_type_form})