from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView

from grafita.models import DevicesGroup


class DeviceGroupForm(forms.ModelForm):
    class Meta:
        model = DevicesGroup
        fields = ['name', 'description', 'admin', 'devices']
        widgets = {
            'devices': forms.CheckboxSelectMultiple(),
        }


class DeviceGroupListCreateView(View):
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


class CreateDeviceGroupView(CreateView):
    model = DevicesGroup
    form_class = DeviceGroupForm
    template_name = 'create_device_group.html'
    success_url = reverse_lazy('device_groups')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


class UpdateDeviceGroupView(UpdateView):
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


class DeviceGroupDetailView(View):
    template_name = 'device_group_detail.html'

    def get(self, request, pk, *args, **kwargs):
        group = get_object_or_404(DevicesGroup, pk=pk)
        return render(request, self.template_name, {'group': group})


class DeleteDeviceGroupView(View):
    template_name = 'delete_device_group.html'
    success_url = reverse_lazy('device_groups')

    def get(self, request, pk, *args, **kwargs):
        group = get_object_or_404(DevicesGroup, pk=pk)
        return render(request, self.template_name, {'group': group})

    def post(self, request, pk, *args, **kwargs):
        group = get_object_or_404(DevicesGroup, pk=pk)
        group.delete()
        return HttpResponseRedirect("/device_groups")
