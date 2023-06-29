from rest_framework import serializers
from .models import Account, Destination

class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ['url', 'http_method', 'headers']

class AccountSerializer(serializers.ModelSerializer):
    destinations = DestinationSerializer(many=True, read_only=True)

    class Meta:
        model = Account
        fields = ['email', 'account_id', 'account_name', 'app_secret_token', 'website', 'destinations']
