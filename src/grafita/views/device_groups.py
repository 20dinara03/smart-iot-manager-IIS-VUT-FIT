from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, UpdateView

from grafita.kpi import kpi_list
from grafita.models import Device, DevicesGroup, DeviceTypeParameter, KPI
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

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and not name.isalnum():
            raise ValidationError('The name must contain only letters and numbers.')
        return name


class KPIForm(forms.ModelForm):
    class_name = forms.ChoiceField(choices=[(k, k) for k in kpi_list()],
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    parameter = forms.ModelChoiceField(
        queryset=DeviceTypeParameter.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control parameter_name'})
    )


    class Meta:
        model = KPI
        fields = ['class_name', 'parameter', 'value']
        widgets = {
            'value': forms.TextInput(attrs={'class': 'form-control'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parameter'].queryset = DeviceTypeParameter.objects.all()

    def clean_value(self):
        value = self.cleaned_data.get('value')
        parameter = self.cleaned_data.get('parameter')

        if parameter:
            min_value = parameter.min_value
            max_value = parameter.max_value

            if value < min_value or value > max_value:
                raise ValidationError(f'Value must be between {min_value} and {max_value}')

        return value


DevicesGroupKPIFormSet = forms.inlineformset_factory(
    DevicesGroup,
    KPI,
    form=KPIForm,
    can_delete=True,
    extra=1
)


class DeviceGroupListView(AuthenticatedUserMixin, View):
    template_name = 'device_groups.html'

    def get(self, request, *args, **kwargs):
        groups = DevicesGroup.objects.all()
        form = DeviceGroupForm()
        return render(request, self.template_name, {'groups': groups, 'form': form})

    @login_required(login_url='/login')
    def device_group_list(request):
        if request.user.is_authenticated:
            groups = DevicesGroup.objects.all()
            form = DeviceGroupForm()
            return render(request, 'device_groups.html', {'groups': groups, 'form': form})
        else:
            return redirect('public_device_group_list')


class CreateDeviceGroupView(AuthenticatedUserMixin, CreateView):
    model = DevicesGroup
    form_class = DeviceGroupForm
    template_name = 'create_device_group.html'
    success_url = reverse_lazy('device_groups')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        context['formset'] = DevicesGroupKPIFormSet()
        return context

    def form_valid(self, form):
        form.instance.admin = self.request.user
        response = super().form_valid(form)
        formset = DevicesGroupKPIFormSet(self.request.POST, instance=self.object)

        for _form in formset:
            device_types = self.object.devices.all().values_list('device_type', flat=True).distinct()

            objects_filter = DeviceTypeParameter.objects.filter(
                device_type__in=device_types
            )
            _form.fields['parameter'].queryset = objects_filter

        if formset.is_valid():
            objs = formset.save(commit=False)
            print(objs)

            for obj in objs:  # type: KPI
                obj.device_group = self.object
                obj.save()
        else:
            print(formset.errors)
            return self.form_invalid(form)

        return response

    def form_invalid(self, form):
        formset = DevicesGroupKPIFormSet(self.request.POST, instance=self.object)
        return self.render_to_response(self.get_context_data(form=form, formset=formset))


class UpdateDeviceGroupView(AuthenticatedUserMixin, UpdateView):
    model = DevicesGroup
    form_class = DeviceGroupForm
    template_name = 'update_device_group.html'
    success_url = reverse_lazy('device_groups')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_object()
        context['group'] = group
        initial_values = {
            'name': group.name,
            'description': group.description,
            'devices': group.devices.all(),
        }
        context['form'] = DeviceGroupForm(instance=group, initial=initial_values)
        if 'formset' not in kwargs:
            context['formset'] = DevicesGroupKPIFormSet(
                instance=group,
                queryset=KPI.objects.filter(device_group=group)
            )
        return context

    def form_valid(self, form):
        form.instance.admin = self.request.user
        request = super().form_valid(form)
        formset = DevicesGroupKPIFormSet(self.request.POST, instance=self.object)

        for _form in formset:
            device_types = self.object.devices.all().values_list('device_type', flat=True).distinct()

            objects_filter = DeviceTypeParameter.objects.filter(
                device_type__in=device_types
            )
            _form.fields['parameter'].queryset = objects_filter

        if formset.is_valid():
            objs = formset.save(commit=False)

            for obj in objs:  # type: KPI
                obj.device_group = self.object
                obj.save()
            return request
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))



class DeviceGroupDetailView(AuthenticatedUserMixin, View):
    template_name = 'device_group_detail.html'

    def get(self, request, pk, *args, **kwargs):
        group = get_object_or_404(DevicesGroup, pk=pk)
        kpis = KPI.objects.filter(device_group=group)
        parameters = list(DeviceTypeParameter.objects.filter(
            device_type__in=group.devices.all().values_list('device_type', flat=True).distinct()
        ).values_list('name', flat=True).distinct())
        can_edit_or_delete = self.request.user == group.admin
        return render(request, self.template_name, {
            "kpis": kpis,
            "parameters": parameters,
            "group": group,
            "can_share": self.request.user == group.admin,
            "can_edit_or_delete": can_edit_or_delete,
            "users": User.objects.all(),
        })

    def post(self, request, pk, *args, **kwargs):
        # on post-request this view behaves that user wants to request access to a group

        # check that user is not admin, does not yet have access to group or did not yet request
        # access
        group = get_object_or_404(DevicesGroup, pk=pk)
        user = request.user

        if request.POST.get("action") == "request":
            if group.shared_with.contains(user) or group.requested_by.contains(user) or user is group.admin:
                return HttpResponseForbidden()

            group.requested_by.add(user)
            group.save()

            return HttpResponseRedirect("/device_groups")
        elif request.POST.get("action") == "grant":
            requested_by = request.POST.get("user")
            if user != group.admin or not requested_by:
                return HttpResponseForbidden()

            requested_user = User.objects.get(pk=requested_by)
            group.requested_by.remove(requested_user)
            group.shared_with.add(requested_user)

            group.save()
            return HttpResponseRedirect("/device_groups")
        return HttpResponseForbidden()


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


def public_device_group_list(request):
    groups = DevicesGroup.objects.all()
    return render(request, 'public_page.html', {'groups': groups})
