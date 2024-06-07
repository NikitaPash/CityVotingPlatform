import os
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib import messages
from azure.storage.blob import BlobServiceClient

from .models import Project, Vote, UserChoice, Comment
from homepage.models import ImageStorage, Notifications
from city_voting_registration.views import send_email


# Show specific project data and votes
@login_required
def detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user = request.user
    user_voted = UserChoice.objects.filter(user=user, project=project)
    comments_query = Comment.objects.filter(project=project)
    comments_query = comments_query.order_by('-pub_date')
    azure_storage_connection_string = os.getenv("connection_str")
    container_name = "profpicscont"
    comments = []
    for comment in comments_query:
        img_object = ImageStorage.objects.filter(user=comment.user).first()
        blob_name = img_object.profile_picture

        blob_service_client = BlobServiceClient.from_connection_string(azure_storage_connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        profile_picture = blob_client.url
        comments.append([profile_picture, comment])
    context = {'comments': comments}
    for message in messages.get_messages(request):
        if message.level == messages.ERROR:
            context['error_message'] = message.message
        elif message.level == messages.SUCCESS:
            context['success_message'] = message.message
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    context['project'] = project
    if user_voted:
        context['user_voted'] = user_voted
    return render(request, 'voting/detail.html', context)


# Vote for a project
@login_required
def vote(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user = request.user
    if project.user == request.user:
        messages.error(request, "You can't vote for yourself")
        return redirect('detail', project_id=project_id)
    user_voted = UserChoice.objects.filter(user=user, project=project)
    if user_voted.exists():
        return redirect('detail', project_id=project_id)
    try:
        selected_choice = project.vote_set.get(pk=request.POST['vote'])
    except (KeyError, Vote.DoesNotExist):
        messages.error(request, 'You did not select a choice')
        return redirect('detail', project_id=project_id)
    else:
        UserChoice.objects.create(user=user, project=project, vote=selected_choice)
        selected_choice.votes += 1
        selected_choice.save()
        user_notifs = Notifications.objects.filter(user=user).first()
        if user_notifs.voting_notifications is True:
            subject = 'Thanks for voting!'
            message = f'Dear {request.user.username}. Thank you for voting for {project.name} project! We appreciate your impact.'
            send_email(request, subject, message)
        messages.success(request, 'Your vote has been recorded successfully.')
        return redirect('detail', project_id=project_id)


# Add comment to a project
@login_required
def add_comment(request, project_id):
    if request.method == 'POST':
        project = Project.objects.get(pk=project_id)
        comment_text = request.POST.get('comment_text', '').strip()
        user_voted = UserChoice.objects.filter(user=request.user, project=project)
        if user_voted:
            if comment_text and user_voted:
                comment = Comment.objects.create(project=project, user=request.user, comment_text=comment_text)
                comment.save()
                user_notifs = Notifications.objects.filter(user=request.user).first()
                if user_notifs.comment_notifications is True:
                    subject = 'Thanks for commenting!'
                    message = f'Dear {request.user.username}. Thank you for leaving a comment under project "{project.name}". We appreciate your opinion.'
                    user_email = request.user.email
                    send_email(request, subject, message, user_email)
                messages.success(request, 'Thanks for commenting!')
                return redirect('detail', project_id=project_id)
            else:
                messages.error(request, 'Comment cannot be empty.')
                return redirect('detail', project_id=project_id)
        else:
            messages.error(request, 'Vote to leave a comment.')
            return redirect('detail', project_id=project_id)
    else:
        return redirect('detail', project_id=project_id)
