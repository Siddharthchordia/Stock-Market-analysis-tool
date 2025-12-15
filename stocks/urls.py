from django.urls import path
from stocks import views

urlpatterns=[
    path("",views.index, name='index'),
    path("<str:ticker>",views.get_stock,name='get-stock'),
    path("autocomplete/", views.stock_autocomplete, name="stock-autocomplete"),
]
