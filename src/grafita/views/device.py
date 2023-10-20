from django import forms
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import CreateView, DetailView, ListView
from grafita.views.types import DeviceTypeForm
from grafita.models import Device, DeviceType


class DeviceForm(forms.ModelForm):
    template_name = "snippets/standard_form.html"

    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )

    class Meta:
        model = Device
        fields = ['name', 'model', 'description', 'location', 'device_group', 'created_by', 'value_min',
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


class DeleteDeviceView(View):
    def post(self, request, pk):
        if request.user.is_authenticated:
            device = get_object_or_404(Device, pk=pk)
            device.delete()
            return HttpResponseRedirect("/devices")
        else:
            raise PermissionDenied("User is not authenticated")


class CreateDeviceView(CreateView):
    model = Device
    form_class = DeviceForm
    template_name = 'create_device.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['device_types'] = DeviceType.objects.all()
        return context
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
        device_form = DeviceForm
        device_type_form = DeviceTypeForm()
        return render(request, 'create_device.html',
                      {'device_form': device_form, 'device_type_form': device_type_form})
