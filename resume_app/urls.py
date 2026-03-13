
from django.urls import path
from .views import home, upload_resume, search_candidate

urlpatterns = [

    path('', home),

    path('upload/', upload_resume),

    path('search/', search_candidate),

]