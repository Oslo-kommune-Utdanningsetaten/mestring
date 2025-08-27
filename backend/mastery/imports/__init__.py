# import os
# import sys

# # Add the backend directory to Python path and setup Django
# script_dir = os.path.dirname(os.path.abspath(__file__))
# backend_dir = os.path.dirname(os.path.dirname(script_dir))
# sys.path.append(backend_dir)

# import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
# django.setup()

# # Import the CLI function
# from .cli import main

# # Always run main when this package is executed
# main()