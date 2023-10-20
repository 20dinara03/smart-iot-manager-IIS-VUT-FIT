from django import forms
from django.views import View
from grafita.models import DeviceType
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, ListView, CreateView
from django.shortcuts import get_object_or_404
from grafita.models import DeviceType, DeviceTypeParameter


# class DeviceTypeForm(forms.ModelForm):
# Define a CharField for attributes to handle the ArrayField
# attributes = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

# class Meta:
# model = DeviceType
# fields = ['name', 'description', 'attributes']

# def clean_attributes(self):
# Convert the input value to a list of strings
# attributes = self.cleaned_data['attributes']
# if attributes:
# attributes = attributes.split(',')
# return attributes

class DeviceTypeForm(forms.ModelForm):
    class Meta:
        model = DeviceType
        fields = ['name', 'description']


class DeviceTypeParameterForm(forms.ModelForm):
    class Meta:
        model = DeviceTypeParameter
        fields = ['name', 'values']


class DeviceTypeList(ListView):
    model = DeviceType
    paginate_by = 100
    template_name = 'Typelist.html'


class DeviceTypeDetail(DetailView):
    model = DeviceType
    template_name = 'device_type_detail.html'


class DeviceTypeCreate(CreateView):
    model = DeviceType
    form_class = DeviceTypeForm
    template_name = 'create_device_type.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["parameter_form"] = DeviceTypeParameterForm()
        return context

    def form_valid(self, form):
        self.object = form.save()

        parameter_form = DeviceTypeParameterForm(self.request.POST)
        if parameter_form.is_valid():
            parameter = parameter_form.save(commit=False)
            parameter.device_type = self.object
            parameter.save()

        return HttpResponseRedirect("/device_types")


class DeviceTypeDelete(View):
    def post(self, request, pk):
        device_type = get_object_or_404(DeviceType, pk=pk)
        device_type.delete()
        return HttpResponseRedirect("/device_types")
