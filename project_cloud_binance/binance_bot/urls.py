from django.urls import path
from django.http import HttpResponse

def home(request):
    return HttpResponse("Django está funcionando!")

urlpatterns = [
    path('', home, name='home'),
]
