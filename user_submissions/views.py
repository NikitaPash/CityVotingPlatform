from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages

from homepage.models import Notifications
from .forms import UserSubmissionForm
from .models import UserSubmission
from voting.models import Project
from city_voting_registration.views import send_email


def is_staff(user):
    return user.is_staff


@login_required
def submit_proposal(request):
    if request.method == "POST":
        form = UserSubmissionForm(request.POST)
        if form.is_valid():
            user = request.user
            submission = form.save(commit=False)
            submission.user = request.user
            user_notifs = Notifications.objects.filter(user=request.user).first()
            if user_notifs.proposal_notifications is True:
                subject = 'Thanks for proposing!'
                message = f'Dear {user.username}. Thank you for proposing your idea! We appreciate your impact.'
                send_email(request, subject, message)
            submission.save()
            messages.success(request, 'Proposal was submitted.')
            return redirect('home')
    else:
        form = UserSubmissionForm()
    return render(request, 'proposal_submission/proposal_form.html', {'form': form})


@login_required
@user_passes_test(is_staff, login_url='/')
def approve_proposal(request, project_id):
    submission = UserSubmission.objects.get(pk=project_id)
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'approve':
            project = Project(name=submission.name,
                              description=submission.description,
                              district=submission.district,
                              user=submission.user
                              )
            submission.is_approved = True
            project.save()
            subject = 'Your project was approved!'
            message = f'Congratulations, {request.user.username}. Your project, {submission.name}, was approved.'
            user_email = submission.user.email
            send_email(request, subject, message, user_email)
            submission.delete()
            messages.success(request, 'Proposal was approved.')
            return redirect('proposals')
        if action == 'reject':
            subject = 'Your project was rejected'
            message = f'Dear {request.user.username}. Unfortunately, your project, {submission.name}, was rejected.'
            user_email = submission.user.email
            send_email(request, subject, message, user_email)
            submission.delete()
            messages.error(request, 'Proposal was rejected.')
            return redirect('proposals')
    else:
        return redirect('proposals')


@login_required
@user_passes_test(is_staff, login_url='/')
def proposals(request):
    proposal_projects = UserSubmission.objects.order_by('-id')
    error_message = None
    success_message = None

    for message in messages.get_messages(request):
        if message.level == messages.ERROR:
            error_message = message.message
        elif message.level == messages.SUCCESS:
            success_message = message.message

    return render(request, "proposal_submission/propose_approval.html", {
        'proposal_projects': proposal_projects,
        'error_message': error_message,
        'success_message': success_message
    })
