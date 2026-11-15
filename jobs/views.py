from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import role_required
from .forms import JobForm, ApplicationForm
from .models import Job, Application


@login_required
def job_list(request):
    jobs = Job.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'jobs/job_list.html', {'jobs': jobs})


@role_required('alumni', verified=True)
def job_create(request):
    form = JobForm(request.POST or None)
    if form.is_valid():
        job = form.save(commit=False)
        job.posted_by = request.user
        job.save()
        messages.success(request, 'Job posted.')
        return redirect('job_list')
    return render(request, 'jobs/job_form.html', {'form': form})


@login_required
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    already_applied = Application.objects.filter(
        job=job, applicant=request.user).exists()
    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'form': ApplicationForm(),
        'already_applied': already_applied,
    })


@role_required('student')
def job_apply(request, pk):
    job = get_object_or_404(Job, pk=pk, is_active=True)
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            app, created = Application.objects.get_or_create(
                job=job, applicant=request.user,
                defaults={'cover_note': form.cleaned_data['cover_note']})
            if created:
                messages.success(request, 'Application submitted.')
            else:
                messages.warning(request, 'You already applied to this job.')
    return redirect('job_detail', pk=pk)


@role_required('alumni')
def job_applications(request, pk):
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    apps = job.applications.select_related('applicant').order_by('-applied_at')
    return render(request, 'jobs/job_applications.html',
                  {'job': job, 'apps': apps})