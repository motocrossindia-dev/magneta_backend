from django.contrib.auth.decorators import login_required


# =====================================================================================================================
# =====================================================================================================================
#                                                       Coupon
# =====================================================================================================================
# =====================================================================================================================
@login_required
def create_coupon(request):
    if request.method == 'POST':
        coupon_name = request.POST.get('coupon_name')
        applicable_discount = int(request.POST.get('applicable_discount'))
        is_type_flat = request.POST.get('is_type_flat') == 'Fixed'
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        is_active = request.POST.get('is_active') == 'on'
        bike_category = request.POST.get('category')
        category_color = request.POST.get('colorPicker')

        # Calculate expiration date if set_duration is on
        if start_date and end_date:
            start_date = date.fromisoformat(start_date)
            end_date = date.fromisoformat(end_date)
            if end_date < start_date:
                return render(request, 'coupon_form.html', {'error_message': 'End date must be after start date'})
        else:
            start_date = end_date = None

        # Create the coupon
        branch_id = request.user
        branch = Branch.objects.get(pk=1)
        # staff = Staff.objects.get(pk=1)
        bike_category = Bike_Category.objects.get(bike_category=bike_category)
        # branch=1
        coupon = Coupon(
            coupon_name=coupon_name,
            branch=branch,
            bike_category=bike_category,
            category_color=category_color,
            company_share=0,
            branch_share=100,
            applicable_discount=applicable_discount,
            is_type_flat=is_type_flat,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active
        )
        coupon.save()
        return redirect('coupon_list')  # Redirect to the coupon list view after creation

    branch = Branch.objects.all()
    bike_categories = Bike_Category.objects.all()

    return render(request, 'coupon_form.html', {'branch': branch, 'bike_categories': bike_categories})


@login_required
def check_coupon_expiry(request):
    today = date.today()
    expired_coupons = Coupon.objects.filter(end_date__lt=today, is_active=True)
    for coupon in expired_coupons:
        coupon.is_active = False
        coupon.is_deleted = True
        coupon.save()


# Coupon List View
@login_required
def coupon_list(request):
    check_coupon_expiry(request)
    coupons = Coupon.objects.filter(is_deleted=False)
    return render(request, 'coupon_list.html', {'coupons': coupons})


@login_required
@csrf_exempt
def activate_coupon(request):
    try:
        coupon_id = request.POST.get('coupon_id')
        coupon = Coupon.objects.get(pk=coupon_id)
        coupon.is_active = True
        coupon.save()
        response_data = {'success': True, 'message': 'Coupon activated successfully'}
    except Coupon.DoesNotExist:
        response_data = {'success': False, 'message': 'Coupon not found'}
    return JsonResponse(response_data)


@login_required
@csrf_exempt
def deactivate_coupon(request):
    try:
        coupon_id = request.POST.get('coupon_id')
        coupon = Coupon.objects.get(pk=coupon_id)
        coupon.is_active = False
        coupon.save()
        response_data = {'success': True, 'message': 'Coupon deactivated successfully'}
    except Coupon.DoesNotExist:
        response_data = {'success': False, 'message': 'Coupon not found'}
    return JsonResponse(response_data)

