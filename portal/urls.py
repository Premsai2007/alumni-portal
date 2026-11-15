path("mentor/request/<int:alumnus_id>/", views.send_request, name="send_request"),
path("mentor/respond/<int:req_id>/<str:decision>/", views.respond_request, name="respond_request"),
path("mentor/requests/", views.my_requests, name="my_requests"),