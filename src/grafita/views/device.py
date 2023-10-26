from django import forms
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from grafita.models import Device


class DeviceForm(forms.ModelForm):
    template_name = "snippets/standard_form.html"

    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )

    class Meta:
        model = Device
        fields = ['name', 'model', 'description', 'location', 'device_group', 'created_by', 'value_min',
                  'value_max', 'default_kpi', 'device_type']
        widgets = {
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


class UpdateDeviceView(UpdateView):
    model = Device
    form_class = DeviceForm
    template_name = 'edit_device.html'
    success_url = '/devices'


class CreateDeviceView(CreateView):
    model = Device
    form_class = DeviceForm
    template_name = 'create_device.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["device_form"] = DeviceForm()
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        # new_device_type = form.cleaned_data.get('new_device_type')

        # if new_device_type:
        # device_type = DeviceType(
        # name=new_device_type,
        # description=data['description']
        # )
        # device_type.save()
        # else:
        # device_type = data['device_type']

        device = Device(
            name=data['name'],
            model=data['model'],
            description=data['description'],
            location=data['location'],
            device_group=data['device_group'],
            created_by=data['created_by'],
            value_min=data['value_min'],
            value_max=data['value_max'],
            default_kpi=data['default_kpi'],
        )
        device.save()

        return HttpResponseRedirect("/devices")
