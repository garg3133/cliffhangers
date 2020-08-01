import ast
import json

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from home.api.serializers import (
    CreateRoadSerializer, CreateImageSerializer,
    CreateIssueDetailSerializer,
)
from home.models import Road, Image, Issue, IssueDetail


@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def create_road(request):
    data = {}

    road_id = request.data['road_id']
    road = Road.objects.filter(road_id=road_id)
    if road.exists():
        data['response'] = 'Road Already exists.'
        data['road_id'] = road[0].id
        return Response(data, status=200)
    else:
        serializer = CreateRoadSerializer(data=request.data)
        if serializer.is_valid():
            road = serializer.save()

            data['response'] = 'Successfully Created'
            data['road_id'] = road.id

            return Response(data, status=201)
        else:
            return Response(serializer.errors)


@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def update_road_image(request):
    data = {}
    image_data = request.data
    issues = ast.literal_eval(image_data['issues'])

    road_id = image_data['road_id']
    road = Road.objects.filter(road_id=road_id).first()
    if road and not Image.objects.filter(road=road, image_id=image_data['image_id']).exists():
        image_serializer = CreateImageSerializer(data=image_data)
        if image_serializer.is_valid():
            image = image_serializer.save(road=road)
            data['response'] = 'Success'
            print(issues)
            for issue in issues:
                issue_name = issue['issue_name']
                count = issue['count']
                quality = issue['quality']

                issue_obj = Issue.objects.filter(name=issue_name)
                if issue_obj.exists():
                    issue_obj = issue_obj[0]
                else:
                    issue_obj = Issue.objects.create(issue_id=issue_name, name=issue_name)

                IssueDetail.objects.create(image=image, issue=issue_obj, count=count, quality=quality)

            return Response(data, status=201)
        else:
            return Response(image_serializer.errors, status=400)
    else:
        data['response'] = 'Error'
        return Response(data, status=400)


@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def update_road_pci(request):
    data = request.data

    road_data = data.pop(road)
    print(road_data)

    return Response({})