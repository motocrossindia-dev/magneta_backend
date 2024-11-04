# import random
# import string
#
#
# def generate_unique_id(self):
#     # Generate zero-padded user ID
#     padded_id = str(self.id).zfill(4)  # Zero-pad the ID to a length of 4
#
#     # Generate a random alphanumeric string of 4 characters for uniqueness
#     random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
#
#     if self.is_distributor:
#         # Create distributor user ID in the format: MAG-CITY-ID-RANDOM
#         return f"MAG-{self.city.upper()}-{padded_id}-{random_suffix}"
#     elif self.is_retailer:
#         return f"MAG-RTL-{padded_id}-{random_suffix}"
#     elif self.is_manager:
#         return f"MAG-MGM-{padded_id}-{random_suffix}"
#     elif self.role == "sales":  # Check if the role is sales
#         return f"SL-{padded_id}-{random_suffix}"  # Format for sales role
#     else:
#         return f"MAG-{padded_id}-{random_suffix}"


# Usage
# self.user_id = self.generate_unique_id()
