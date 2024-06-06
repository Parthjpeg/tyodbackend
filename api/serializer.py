from rest_framework import serializers

from .models import *

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'

class fileSerializer(serializers.ModelSerializer):
    class Meta:
        model = files
        fields = '__all__'

class filecontentSerializer(serializers.ModelSerializer):
    class Meta:
        model = filecontent
        fields = '__all__'


class exexcelfilecontentSerializer(serializers.ModelSerializer):
    class Meta:
        model = excelfilecontent
        fields = '__all__'
