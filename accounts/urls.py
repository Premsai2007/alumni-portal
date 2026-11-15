from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile_view, name='profile_detail'),
    path('alumni-area/', views.alumni_area, name='alumni_area'),
    path("alumni/", views.alumni_list, name="alumni_list"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("analytics/", views.analytics, name="analytics"),
    path("mentor/request/<int:alumnus_id>/", views.send_request, name="send_request"),
    path("mentor/respond/<int:req_id>/<str:decision>/", views.respond_request, name="respond_request"),
    path("mentor/requests/", views.my_requests, name="my_requests"),
    path("analytics/", views.analytics, name="analytics"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
