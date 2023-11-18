from django.contrib.auth.mixins import UserPassesTestMixin


class AuthenticatedUserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated
