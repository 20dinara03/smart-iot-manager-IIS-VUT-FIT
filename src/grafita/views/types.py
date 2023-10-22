from django import forms
from django.views.generic import DetailView
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False


class DeviceTypeParameterForm(forms.ModelForm):
    class Meta:
        model = DeviceTypeParameter
        fields = ['name', 'values']


#class DeviceTypeList(ListView):
    #model = DeviceType
    #paginate_by = 100
    #template_name = 'typelist.html'


class DeviceTypeDetail(DetailView):
    model = DeviceType
    template_name = 'device_type_detail.html'


