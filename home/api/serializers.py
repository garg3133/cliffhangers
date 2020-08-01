from rest_framework import serializers

from home.models import Road, Image, IssueDetail

class CreateRoadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Road
        fields = ['road_id', 'pci', 'district', 'state', 'total_images']

class CreateImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image_id', 'image', 'quality']

class CreateIssueDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueDetail
        fields = ['count', 'quality']