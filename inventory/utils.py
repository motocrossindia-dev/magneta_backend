from datetime import timedelta
from django.utils import timezone
from .models import GoodsReturnNote  # Replace with the actual path to your models

# =============

# =============

def generate_grn_number():
    # Get the start of the current month
    today_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    print(f"[DEBUG] Start of the current month: {today_start}")

    # Get the end of the current month
    next_month = today_start.replace(day=28) + timedelta(days=4)  # this will never fail
    today_end = next_month - timedelta(days=next_month.day - 1)
    print(f"[DEBUG] End of the current month: {today_end}")

    # Get the last GRN number for the current month
    last_grn = GoodsReturnNote.objects.filter(created__range=(today_start, today_end)).order_by('-GRNnumber').first()
    print(f"[DEBUG] Last GRN entry for the current month: {last_grn}")

    # Determine the new GRN number
    if last_grn and last_grn.GRNnumber:
        last_grn_number = int(last_grn.GRNnumber.split('-')[-1]) + 1
        print(f"[DEBUG] Last GRN number found: {last_grn.GRNnumber}")
        print(f"[DEBUG] Incremented GRN number: {last_grn_number}")
    else:
        last_grn_number = 1
        print(f"[DEBUG] No GRN found for the current month. Starting with GRN number: 001")

    # Ensure the number doesn't exceed 999
    if last_grn_number > 999:
        print(f"[ERROR] Maximum GRN numbers exceeded for the month.")
        raise ValueError("Maximum GRN numbers exceeded for the month.")

    # Generate the new GRN number with the desired format
    grn_number = f"GRN-{today_start.strftime('%Y%m')}-{last_grn_number:03d}"
    print(f"[DEBUG] Generated GRN number: {grn_number}")

    return grn_number

# # Usage example:
# grn_data = {}
# grn_data['GRNnumber'] = generate_grn_number()
