from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateformat import format

from city_map.models import DistrictInfo
from voting.models import Project


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project_info(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    formatted_pub_date = format(project.pub_date, 'Y-m-d H:i')
    context = {'Name': project.name,
               'Created by': project.user.username,
               'Description': project.description,
               'District': project.district,
               'Published': formatted_pub_date}

    return Response(context, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request, username):
    user = get_object_or_404(User, username=username)
    context = {'Username': user.username,
               'Email': user.email,
               'Is staff': user.is_staff,
               }
    return Response(context, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_projects(request):
    projects = Project.objects.all().order_by('-id')
    print(projects)
    context = []
    for project in projects:
        formatted_pub_date = format(project.pub_date, 'Y-m-d H:i')
        project_data = {
            'Id': project.id,
            'Name': project.name,
            'Created by': project.user.username,
            'Description': project.description,
            'District': project.district,
            'Published': formatted_pub_date
        }
        context.append(project_data)

    return Response({'All projects': context}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_districts(request):
    districts = DistrictInfo.objects.all().order_by('-id')
    context = []
    for district in districts:
        district_data = {
            'Name': district.name,
            'Population': district.population,
            'Area': district.area,
            'Administration': district.administration,
            'Administration contact data': district.administration_contact
        }
        context.append(district_data)
    return Response({'All districts': context}, status=status.HTTP_200_OK)
