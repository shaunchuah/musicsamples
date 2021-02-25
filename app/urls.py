from django.urls import path, re_path, include
from app import views
from rest_framework import routers, serializers, viewsets
from .views import SampleViewSet, SampleIsFullyUsedViewSet
from django.conf.urls import handler404, handler500

router = routers.DefaultRouter()
router.register(r'samples', SampleViewSet)
router.register(r'samples_used', SampleIsFullyUsedViewSet)

handler404 = 'app.views.error_404'
handler500 = 'app.views.error_500'

urlpatterns = [
    path('', views.index, name='home'),
    path('analytics/', views.analytics, name='analytics'),
    path('analytics/gid_overview', views.gid_overview, name='gid_overview'),
    path('reference/', views.reference, name='reference'),
    path('archive/', views.archive, name='archive'),
    path('used_samples/', views.used_samples, name='used_samples'),
    path('add/', views.add, name='new_sample'),
    path('samples/<int:pk>/', views.sample_detail, name='sample_detail'),
    path('samples/<int:pk>/edit/', views.sample_edit, name='sample_edit'),
    path('samples/<int:pk>/delete/', views.delete, name='delete'),
    path('samples/<int:pk>/restore/', views.restore, name='restore'),
    path('samples/<int:pk>/fully_used/', views.fully_used, name='fully_used'),
    path('samples/<int:pk>/reactivate_sample/', views.reactivate_sample, name='reactivate_sample'),
    path('samples/<int:pk>/checkout/', views.checkout, name='checkout'),
    path('search/', views.search, name="search"),
    path('export_csv/', views.export_csv, name='export_csv'),
    path('export_excel/', views.export_excel, name='export_excel'),
    path('account/', views.account, name='account'),
    path('notes/', views.notes, name='notes'),
    path('notes/<int:pk>/', views.note_detail, name='note_detail'),
    path('notes/add/', views.note_add, name='new_note'),
    path('notes/<int:pk>/edit/', views.note_edit, name='note_edit'),
    path('notes/<int:pk>/delete/', views.note_delete, name='note_delete'),
    path('notes/personal/', views.notes_personal, name='note_personal'),
    path('notes/tag/<slug>', views.note_tags, name='note_tags'),
    path('notes/authors/<int:pk>', views.note_authors, name='note_authors'),
    path('autocomplete/locations/', views.autocomplete_locations, name='autocomplete_locations'),
    path('autocomplete/patients/', views.autocomplete_patient_id, name='autocomplete_patients'),
    path('autocomplete/tags/', views.autocomplete_tags, name='autocomplete_tags'),
    path('notes/search/', views.search_notes, name='search_notes'),
    path('api/', include(router.urls)),
    path('barcode/', views.barcode, name='barcode'),
    path('barcode/samples_used/', views.barcode_samples_used, name='barcode_samples_used')
]

