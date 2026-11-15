from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import role_required
from .forms import ProfileForm, RegisterForm
from .models import Profile
from events.models import EventRegistration
from events.models import EventRegistration
from .models import MentorshipRequest
from .models import Announcement


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.profile.role == 'alumni':
                messages.info(request, 'Registered! Your account is pending admin approval.')
            else:
                messages.success(request, 'Registered! You can log in now.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request, username=None):
    user = get_object_or_404(User, username=username) if username else request.user
    return render(request, 'accounts/profile.html',
                  {'profile_user': user, 'profile': user.profile,
                   'is_own': user == request.user})


@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile_edit.html', {'form': form})


# Placeholder to test role restriction (real alumni pages come on later days)
@role_required('alumni', verified=True)
def alumni_area(request):
    return HttpResponse('Welcome, verified alumnus!')
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from .models import Profile

@login_required
def alumni_list(request):
    qs = (Profile.objects
          .filter(role="alumni", is_verified=True)   # verified only
          .select_related("user")
          .order_by("user__first_name"))

    name = request.GET.get("name", "").strip()
    batch = request.GET.get("batch", "").strip()
    department = request.GET.get("department", "").strip()
    company = request.GET.get("company", "").strip()
    skills = request.GET.get("skills", "").strip()

    if name:
        qs = qs.filter(Q(user__first_name__icontains=name) |
                       Q(user__last_name__icontains=name) |
                       Q(user__username__icontains=name))
                        
    if batch:
        qs = qs.filter(batch_year=batch)
    if department:
        qs = qs.filter(department__icontains=department)
    if company:
        qs = qs.filter(company__icontains=company)
    if skills:
        qs = qs.filter(skills__icontains=skills)

    page_obj = Paginator(qs, 10).get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)          # keep filters when changing page

    return render(request, "accounts/alumni_list.html", {
        "page_obj": page_obj,
        "querystring": params.urlencode(),
        "filters": request.GET,
    })
from django.db.models import Count
from jobs.models import Job, Application
from events.models import EventRegistration

@login_required
def dashboard(request):
    role = getattr(getattr(request.user, "profile", None), "role", None)
    ctx = {
        "my_events": EventRegistration.objects
                     .filter(user=request.user).select_related("event")
                     .order_by("event__date"),
        "my_applications": None,
        "my_jobs": None,
    }
    if role == "student":
        ctx["my_applications"] = (Application.objects
                                  .filter(applicant=request.user)
                                  .select_related("job").order_by("-applied_at"))
    if role == "alumni":
        ctx["my_jobs"] = (Job.objects.filter(posted_by=request.user)
                          .annotate(app_count=Count("applications")))
    return render(request, "accounts/dashboard.html", ctx)
import pandas as pd
import plotly.express as px
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from events.models import EventRegistration

@staff_member_required
def analytics(request):
    df = pd.DataFrame(Profile.objects.filter(role="alumni")
                      .values("batch_year", "department", "company"))
    charts = {}
    if not df.empty:
        b = df["batch_year"].value_counts().sort_index().reset_index()
        b.columns = ["batch_year", "count"]
        charts["batch"] = px.bar(b, x="batch_year", y="count", title="Alumni per Batch"
                                 ).to_html(full_html=False, include_plotlyjs="cdn")

        d = df["department"].value_counts().reset_index()
        d.columns = ["department", "count"]
        charts["dept"] = px.pie(d, names="department", values="count", title="Alumni per Department"
                                ).to_html(full_html=False, include_plotlyjs=False)

        c = df["company"].value_counts().head(10).reset_index()
        c.columns = ["company", "count"]
        charts["company"] = px.bar(c, x="count", y="company", orientation="h", title="Top 10 Companies"
                                   ).to_html(full_html=False, include_plotlyjs=False)

    reg = pd.DataFrame(EventRegistration.objects.values("event__title"))
    if not reg.empty:
        r = reg["event__title"].value_counts().reset_index()
        r.columns = ["event", "registrations"]
        charts["events"] = px.bar(r, x="event", y="registrations", title="Event Registrations"
                                  ).to_html(full_html=False, include_plotlyjs=False)

    return render(request, "accounts/analytics.html", {"charts": charts})
@login_required
def send_request(request, alumnus_id):
    if request.method == "POST" and alumnus_id != request.user.id:
        MentorshipRequest.objects.get_or_create(
            student=request.user, alumnus_id=alumnus_id,
            defaults={"message": request.POST.get("message", "")})
        messages.success(request, "Mentorship request sent.")
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
    sent = MentorshipRequest.objects.filter(student=request.user).select_related("alumnus")
    received = MentorshipRequest.objects.filter(alumnus=request.user).select_related("student")
    announcements = Announcement.objects.order_by("-created_at")[:5]
    return render(request, "accounts/my_requests.html", {"sent": sent, "received": received,"announcements": announcements})
@staff_member_required
def analytics(request):
    df = pd.DataFrame(Profile.objects.filter(role="alumni")
                      .values("batch_year", "department", "company"))
    charts = {}
    if not df.empty:
        b = df["batch_year"].value_counts().sort_index().reset_index()
        b.columns = ["batch_year", "count"]
        charts["batch"] = px.bar(b, x="batch_year", y="count", title="Alumni per Batch"
                                 ).to_html(full_html=False, include_plotlyjs="cdn")

        d = df["department"].value_counts().reset_index()
        d.columns = ["department", "count"]
        charts["dept"] = px.pie(d, names="department", values="count", title="Alumni per Department"
                                ).to_html(full_html=False, include_plotlyjs=False)

        c = df["company"].value_counts().head(10).reset_index()
        c.columns = ["company", "count"]
        charts["company"] = px.bar(c, x="count", y="company", orientation="h", title="Top 10 Companies"
                                   ).to_html(full_html=False, include_plotlyjs=False)

    reg = pd.DataFrame(EventRegistration.objects.values("event__title"))
    if not reg.empty:
        r = reg["event__title"].value_counts().reset_index()
        r.columns = ["event", "registrations"]
        charts["events"] = px.bar(r, x="event", y="registrations", title="Event Registrations"
                                  ).to_html(full_html=False, include_plotlyjs=False)

    return render(request, "accounts/analytics.html", {"charts": charts})
def recommend_mentors(student_profile, top_n=5):
    student_skills = {s.strip().lower() for s in student_profile.skills.split(",") if s.strip()}
    rows = []
    for a in Profile.objects.filter(role="alumni"):
        alumni_skills = {s.strip().lower() for s in a.skills.split(",") if s.strip()}
        shared = student_skills & alumni_skills
        union = student_skills | alumni_skills
        rows.append({"alumnus": a, "shared": len(shared),
                     "score": len(shared) / len(union) if union else 0})
    df = pd.DataFrame(rows).sort_values(["shared", "score"], ascending=False)
    return df.head(top_n)