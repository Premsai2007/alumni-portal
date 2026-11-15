from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import EventForm
from .models import Event, EventRegistration
from .models import Profile
from events.models import EventRegistration
@login_required
def event_list(request):
    events = Event.objects.filter(date__gte=timezone.now()).order_by("date")
    registered_ids = set(EventRegistration.objects
                         .filter(user=request.user).values_list("event_id", flat=True))
    return render(request, "events/event_list.html",
                  {"events": events, "registered_ids": registered_ids})

@user_passes_test(lambda u: u.is_authenticated and (u.is_staff or getattr(getattr(u, "profile", None), "role", None) == "admin"))
def event_create(request):
    form = EventForm(request.POST or None)
    if form.is_valid():
        ev = form.save(commit=False)
        ev.created_by = request.user
        ev.save()
        messages.success(request, "Event created.")
        return redirect("event_list")
    return render(request, "events/event_form.html", {"form": form})

@login_required
def event_register(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        _, created = EventRegistration.objects.get_or_create(event=event, user=request.user)
        messages.success(request, "Registered!" if created else "You're already registered.")
    return redirect("event_list")