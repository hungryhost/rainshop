import rest_framework_simplejwt
from django.http import Http404
from rest_framework.views import exception_handler
from rest_framework import exceptions


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, exceptions.NotAuthenticated):
        response.data = {}
        errors = ["Authentication not provided."]
        response.data['Unauthorized'] = errors

        return response
    if isinstance(exc, Http404):
        response.data = {}
        errors = ["Resource does not exist"]
        response.data['Not Found'] = errors

        return response
    if isinstance(exc, rest_framework_simplejwt.exceptions.InvalidToken):
        response.data = {}
        errors = ["Given token is not valid"]
        response.data['Invalid Token'] = errors

        return response
    if isinstance(exc, exceptions.PermissionDenied):
        response.data = {}
        errors = ['You do not have necessary permissions']
        response.data['Forbidden'] = errors

    return response
