from django.urls import path
from .views import GuideListView

urlpatterns = [
    path('guides/', GuideListView.as_view(), name='list-guides'),
]
