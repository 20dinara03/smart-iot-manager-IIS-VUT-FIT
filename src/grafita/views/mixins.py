from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse


class AuthenticatedUserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated


class StaffMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, "Only the administrator has access to this data.")
        return HttpResponseRedirect(reverse('device_groups'))
