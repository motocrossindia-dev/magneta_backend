from rest_framework.permissions import BasePermission


class IsManagerPermission(BasePermission):

    def has_permission(self, request, view):
        # Check if the user is authenticated and is an organizer
        return request.user.is_authenticated and request.user.is_manager


class IsDistributorPermission(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated and is an organizer
        return request.user.is_authenticated and request.user.is_distributor


class IsManagerOrDistributorPermission(BasePermission):

    def has_permission(self, request, view):
        # Check if the user is authenticated and is an organizer
        return request.user.is_authenticated and (request.user.is_manager or request.user.is_distributor)


class IsRetailerPermission(BasePermission):

    def has_permission(self, request, view):
        # Check if the user is authenticated and is an organizer
        return request.user.is_authenticated and request.user.is_retailer


class IsManagerOrDistributorOrRetailerPermission(BasePermission):

    def has_permission(self, request, view):
        # Check if the user is authenticated and is an organizer
        return request.user.is_authenticated and (
                request.user.is_manager or request.user.is_distributor or request.user.is_retailer)


class IsStoreManagerPermission(BasePermission):

    def has_permission(self, request, view):
        # Check if the user is authenticated and is an organizer
        return request.user.is_authenticated
