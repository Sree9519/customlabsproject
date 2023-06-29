from rest_framework import viewsets
from rest_framework.response import Response
import requests
from django.shortcuts import get_object_or_404
from .models import Account, Destination
from .serializers import AccountSerializer, DestinationSerializer
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer

    def perform_create(self, serializer):
        account = get_object_or_404(Account, pk=self.kwargs['account_id'])
        serializer.save(account=account)


@csrf_exempt
def incoming_data_api(request):
    if request.method == 'POST':
        app_secret_token = request.headers.get('CL-X-TOKEN')
        if not app_secret_token:
            return JsonResponse({'error': 'Unauthenticated'}, status=401)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid Data'}, status=400)

        account = get_object_or_404(Account, app_secret_token=app_secret_token)

        for destination in account.destinations.all():
            headers = destination.headers
            headers['Content-Type'] = 'application/json'
            headers['Accept'] = '*'
            if destination.http_method == 'GET':
                params = {'data': json.dumps(data)}
                response = requests.get(destination.url, headers=headers, params=params)
            else:
                response = requests.request(destination.http_method, destination.url, headers=headers, json=data)

            print(f'Response from {destination.url}: {response.status_code}')

        return JsonResponse({'status': 'success'})

    return JsonResponse({'error': 'Method Not Allowed'}, status=405)
