from django.contrib import admin
from django.urls import path, include


# ==========================================
# URL UTAMA PROJECT PRESENLY
# ==========================================

urlpatterns = [

    # Halaman Admin Django
    path(
        'admin/',
        admin.site.urls
    ),

    # Seluruh endpoint REST API Presenly
    path(
        'api/',
        include('core.urls')
    ),

]