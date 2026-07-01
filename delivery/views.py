from django.shortcuts import render, get_object_or_404
from django.http import Http404, FileResponse, HttpResponseRedirect
from django.contrib import messages
from .models import DeliveryToken
from .services import get_download_response


def download_file(request, token):
    try:
        response = get_download_response(token, request)
        if response is None:
            return render(request, 'delivery/token_expired.html', status=404)
        return response
    except Http404:
        return render(request, 'delivery/token_expired.html', status=404)


def download_expired(request):
    return render(request, 'delivery/token_expired.html')
