# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from app import views

urlpatterns = [
    # Matches any html file 
    re_path(r'^.*\.html', views.pages, name='pages'),

    # The home page
    path('', views.index, name='home'),
    path('analytics/', views.analytics, name='analytics'),
    path('add/', views.add, name='new_sample'),
    path('samples/<int:pk>/', views.sample_detail, name='sample_detail'),
    path('samples/<int:pk>/edit/', views.sample_edit, name='sample_edit'),
    path('samples/<int:pk>/checkout/', views.checkout, name='checkout'),
    path('search/', views.search, name="search"),
    path('bulkadd/', views.bulkadd, name='bulkadd'),
    path('export_csv/', views.export_csv, name='export_csv'),
]
