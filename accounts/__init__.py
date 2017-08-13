from django.views.generic import ListView
from django.contrib.auth.models import User

class UserListView(ListView):
    template_name = 'user/userlist.html'
    model = User
    paginate_by = 6
