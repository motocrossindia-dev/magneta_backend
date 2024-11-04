from django.http import JsonResponse
from rest_framework.decorators import api_view

from update_app.models import AppVersionNumber, PartnerAppVersionNumber, IphoneAppVersionNumber, \
    IphonePartnerAppVersionNumber


@api_view(['GET'])
def get_build_number(request):
    try:
        latest_version = AppVersionNumber.objects.latest('created')
        data = {
            'latest_version': latest_version.latest_version,
            'note': latest_version.note,
            'force_update': latest_version.force_update,
            'base_version': latest_version.base_version
        }
        return JsonResponse(data)
    except AppVersionNumber.DoesNotExist:
        return JsonResponse({'error': 'No build numbers available'}, status=404)
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Unexpected error'}, status=404)


@api_view(['GET'])
def get_partner_build_number(request):
    try:
        latest_version = PartnerAppVersionNumber.objects.latest('created')
        data = {
            'latest_version': latest_version.latest_version,
            'note': latest_version.note,
            'force_update': latest_version.force_update,
            'base_version': latest_version.base_version
        }
        return JsonResponse(data)
    except AppVersionNumber.DoesNotExist:
        return JsonResponse({'error': 'No Partner build numbers available'}, status=404)
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Unexpected error'}, status=404)


@api_view(['GET'])
def iphone_get_build_number(request):
    try:
        latest_version = IphoneAppVersionNumber.objects.latest('created')
        data = {
            'latest_version': latest_version.latest_version,
            'note': latest_version.note,
            'force_update': latest_version.force_update,
            'base_version': latest_version.base_version
        }
        return JsonResponse(data)
    except IphoneAppVersionNumber.DoesNotExist:
        return JsonResponse({'error': 'No build numbers available'}, status=404)
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Unexpected error'}, status=404)


@api_view(['GET'])
def iphone_get_partner_build_number(request):
    try:
        latest_version = IphonePartnerAppVersionNumber.objects.latest('created')
        data = {
            'latest_version': latest_version.latest_version,
            'note': latest_version.note,
            'force_update': latest_version.force_update,
            'base_version': latest_version.base_version
        }
        return JsonResponse(data)
    except IphonePartnerAppVersionNumber.DoesNotExist:
        return JsonResponse({'error': 'No Partner build numbers available'}, status=404)
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Unexpected error'}, status=404)
