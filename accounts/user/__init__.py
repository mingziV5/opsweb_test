from django.views.generic import ListView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from . import views

class UserListView(LoginRequiredMixin, ListView):
    template_name = 'user/userlist.html'
    model = User
    paginate_by = 8
