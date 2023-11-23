from django import forms
from django.core.exceptions import PermissionDenied
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import DetailView, ListView, FormView, UpdateView
from grafita.models import DeviceType, DeviceTypeParameter
from grafita.views.mixins import AuthenticatedUserMixin


class DeviceTypeForm(forms.ModelForm):
    class Meta:
        model = DeviceType
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }


class DeviceTypeParameterForm(forms.ModelForm):
    class Meta:
        model = DeviceTypeParameter
        fields = ['name', 'min_value', 'max_value']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'min_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_value': forms.NumberInput(attrs={'class': 'form-control'}),
        }


DeviceTypeParameterFormSet = inlineformset_factory(
    DeviceType,
    DeviceTypeParameter,
    form=DeviceTypeParameterForm,
    can_delete=False,
    extra=1,
)


class DeleteDeviceTypeView(AuthenticatedUserMixin, View):
    def post(self, request, pk):
        if request.user.is_authenticated:
            device_type = get_object_or_404(DeviceType, pk=pk)
            device_type.delete()
            return HttpResponseRedirect("/device_types")
        else:
            raise PermissionDenied("User is not authenticated")


class UpdateDeviceTypeView(AuthenticatedUserMixin, UpdateView):
    model = DeviceType
    form_class = DeviceTypeForm
    template_name = 'device_type_create.html'
    success_url = '/device_types'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['parameter_formset'] = DeviceTypeParameterFormSet(self.request.POST, instance=self.object)
        else:
            context['action'] = 'Update'
            context['parameter_formset'] = DeviceTypeParameterFormSet(instance=self.object,
                                                                      queryset=DeviceTypeParameter.objects.filter(
                                                                          device_type=self.object))
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        parameter_formset = context['parameter_formset']

        if parameter_formset and parameter_formset.is_valid():
            self.object = form.save()  # Save the DeviceType instance

            # Save the parameters
            instances = parameter_formset.save(commit=False)

            # Handle deleted parameters
            for instance in parameter_formset.deleted_objects:
                instance.delete()

            # Set the DeviceType for the remaining instances
            for instance in instances:
                instance.device_type = self.object
                instance.save()

            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class DeviceTypeCreate(AuthenticatedUserMixin, FormView):
    form_class = DeviceTypeForm
    template_name = 'device_type_create.html'
    success_url = '/device_types/'

    def get_context_data(self, **kwargs):
        if self.request.POST:
            kwargs['parameter_formset'] = DeviceTypeParameterFormSet(self.request.POST)
        else:
            kwargs['action'] = 'Create'
            kwargs['parameter_formset'] = DeviceTypeParameterFormSet()

        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        parameter_formset = context['parameter_formset']

        if parameter_formset and parameter_formset.is_valid():
            device_type = form.save(commit=False)
            device_type.save()

            for parameter_form in parameter_formset:
                if parameter_form.cleaned_data and not all(parameter_form.cleaned_data.values()):
                    parameter = parameter_form.save(commit=False)
                    parameter.device_type = device_type
                    parameter.save()

            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class DeviceTypeList(AuthenticatedUserMixin, ListView):
    model = DeviceType
    paginate_by = 100
    template_name = 'device_types.html'


class DeviceTypeDetail(AuthenticatedUserMixin, DetailView):
    model = DeviceType
    template_name = 'device_type_detail.html'
