from django.contrib.auth.models import Group, User
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView
from grafita.views.mixins import StaffMixin


class Users(StaffMixin, ListView):
    model = User
    template_name = 'admin/user.html'


class UserDetail(StaffMixin, DetailView):
    model = User
    template_name = 'admin/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.all()
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()  # type: ignore
        context = self.get_context_data(object=self.object)
        context['user'] = request.user
        return self.render_to_response(context)

    @staticmethod
    def post(request, pk: int):
        user: User = User.objects.get(device_pk=pk)
        data = request.POST
        if data['password']:
            user.set_password(data['password'])
        user.email = data['email']
        user.first_name = data['first_name']
        user.last_name = data['last_name']

        user.save()
        return redirect('user', pk=pk)


def update_user_groups(request, pk: int):
    user: User = User.objects.get(id=pk)
    data = request.POST
    groups_id: list[int] = data.getlist('groups')
    groups: list[Group] = Group.objects.filter(pk__in=groups_id)

    user.groups.set(groups)

    user.save()
    return redirect('user', pk=pk)
