from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import MentorshipRequest

@login_required
def send_request(request, alumnus_id):
    if request.method == "POST":
        MentorshipRequest.objects.get_or_create(
            student=request.user, alumnus_id=alumnus_id,
            defaults={"message": request.POST.get("message", "")})
    return redirect("my_requests")

@login_required
def respond_request(request, req_id, decision):
    req = get_object_or_404(MentorshipRequest, id=req_id, alumnus=request.user)
    if decision in ("accepted", "rejected"):
        req.status = decision
        req.save()
    return redirect("my_requests")

@login_required
def my_requests(request):
    sent = MentorshipRequest.objects.filter(student=request.user)
    received = MentorshipRequest.objects.filter(alumnus=request.user)
    return render(request, "portal/my_requests.html", {"sent": sent, "received": received})