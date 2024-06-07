from azure.storage.blob import BlobServiceClient
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import os

from .models import ImageStorage, Notifications
from .forms import ProfilePictureForm, NotificationsForm
from voting.models import Project


def home(request):
    query = request.GET.get('q')
    project_list = Project.objects.all()

    if query:
        project_list = project_list.filter(Q(name__icontains=query))

    project_list = project_list.order_by('-pub_date')
    paginator = Paginator(project_list, 5)

    page = request.GET.get('page')
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        projects = paginator.page(1)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)

    context = {'projects': projects}
    for message in messages.get_messages(request):
        if message.level == messages.ERROR:
            context['error_message'] = message.message
        elif message.level == messages.SUCCESS:
            context['success_message'] = message.message
    return render(request, "homepage/projects.html", context)


@login_required
def profile(request):
    azure_storage_connection_string = os.getenv("connection_str")
    container_name = "profpicscont"
    userpic = ImageStorage.objects.filter(user=request.user).first()
    if not userpic:
        userpic = ImageStorage.objects.create(user=request.user)
        userpic.save()
    blob_name = userpic.profile_picture

    blob_service_client = BlobServiceClient.from_connection_string(azure_storage_connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    profile_picture = blob_client.url
    context = {'profile_picture': profile_picture}

    for message in messages.get_messages(request):
        if message.level == messages.ERROR:
            context['error_message'] = message.message
        elif message.level == messages.SUCCESS:
            context['success_message'] = message.message
    form = NotificationsForm(instance=Notifications.objects.filter(user=request.user).first())
    context['notification_form'] = form
    return render(request, "homepage/profile.html", context)


@login_required
def update_username(request):
    if request.method == 'POST':
        new_username = request.POST.get('new_username')
        if new_username:
            if request.user.username == new_username:
                messages.error(request, "New username is identical to the old one.")
                return redirect('profile')
            users = User.objects.filter(username=new_username)
            if users:
                messages.error(request, 'Username is already taken.')
                return redirect('profile')
            request.user.username = new_username
            request.user.save()
            messages.success(request, 'Username has been changed.')
            return redirect('profile')
        else:
            messages.error(request, 'Username cannot be empty.')
            return redirect('profile')
    return redirect('profile')


@login_required
def update_profile_picture(request):
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.container_name = 'profpicscont'
            profile_picture = form.cleaned_data['profile_picture']
            existing_image = ImageStorage.objects.filter(user=request.user).first()
            if existing_image:
                if existing_image.profile_picture != 'default_profile_picture.png':
                    existing_image.profile_picture.delete()
                existing_image.profile_picture = profile_picture
                existing_image.save()
            else:
                ImageStorage.objects.create(user=request.user, profile_picture=profile_picture)
            messages.success(request, 'Profile picture has been changed.')
            return redirect('profile')
        else:
            messages.error(request, 'Error updating profile picture. Please try again.')
            return redirect('profile')
    else:
        return redirect('profile')


@login_required
def update_notification_settings(request):
    notifications_instance = Notifications.objects.filter(user=request.user).first()
    if request.method == 'POST':
        form = NotificationsForm(request.POST, instance=notifications_instance)
        if form.is_valid():
            notif_changes = form.save(commit=False)
            notif_changes.user = request.user
            notif_changes.save()
            messages.success(request, 'Notification settings were changed.')
            return redirect('profile')
    else:
        return redirect('profile')
