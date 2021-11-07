from rest_framework import permissions


class CartOwner(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		if obj.user == request.user or request.user.is_superuser:
			return True
		return False

