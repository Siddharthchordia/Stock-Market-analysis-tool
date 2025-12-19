from django.urls import path
from stocks import views
from django.http import HttpResponse

def health(request):
    return HttpResponse('ok')

urlpatterns=[
    path("",views.index, name='index'),
    path("company/<str:ticker>",views.get_stock,name='get-stock'),
    path("autocomplete/", views.stock_autocomplete, name="stock-autocomplete"),
    path("health/", health),
]
