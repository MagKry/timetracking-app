# Timetracking-app
The web application created with use of framework Django that enables logged in users, to log the time they spent on certain activities during their work day.

There are 4 types of user groups with diverse permissions.
- standard user: can log and view their own hours, can view the list of all employees.
- manager user: can also view the list hours of the employees that belong to their department, view summarised hours per department and per sales channel (as the list and on the chart), can add user
- director user: on top of manager permissions, director can view the data for all departments
- admin: has all above permissions, but also can delete and edit hours and users

Hours added in the app can be filtered based on dates (all, current week, current month, current year).

Bootstrap has been used for frontend.
Models have been registered in django-admin.
