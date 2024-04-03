# from .models import LoggedHours
#
#
# def get_context_data_hours_per_sales_channel(request):
#     employee_entries = LoggedHours.objects.filter(employee=request.user)
#     hours_per_channel = {}
#     for entry in employee_entries:
#         sales_channel = entry.sales_channel
#         hours = entry.hour
#         if sales_channel in hours_per_channel:
#             hours_per_channel[sales_channel] += hours
#         else:
#             hours_per_channel[sales_channel] = hours
#     return hours_per_channel