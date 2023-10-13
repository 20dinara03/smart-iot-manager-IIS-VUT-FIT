from django import forms
from grafita.models import DeviceType
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, ListView
from django.shortcuts import get_object_or_404


class DeviceTypeForm(forms.ModelForm):
    # Define a CharField for attributes to handle the ArrayField
    attributes = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = DeviceType
        fields = ['name', 'description', 'attributes']

    def clean_attributes(self):
        # Convert the input value to a list of strings
        attributes = self.cleaned_data['attributes']
        if attributes:
            attributes = attributes.split(',')
        return attributes


class DeviceTypeList(ListView):
    model = DeviceType
    paginate_by = 100
    form_class = DeviceTypeForm
    template_name = 'Typelist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class()
        return context

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # Create a list from the attributes field input
            attributes = data.pop('attributes', [])
            device_type = DeviceType(**data)
            device_type.attributes = attributes
            device_type.save()

        return HttpResponseRedirect("/create_device")


class DeviceTypeDetail(DetailView):
    model = DeviceType

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            action = request.POST.get("action")
            if action == "delete":
                return self.delete(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def delete(_, device_type_id: int):
        device_type = get_object_or_404(DeviceType, id=device_type_id)
        device_type.delete()
        return HttpResponseRedirect("/create_device")