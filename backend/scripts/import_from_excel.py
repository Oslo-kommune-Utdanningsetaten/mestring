import os
import sys
import argparse
import pandas as pd

# bootstrap Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from mastery import models

def import_sheet(data_frame, model, key_field, field_map):
    for _, row in data_frame.iterrows():
        lookup = {key_field: row[key_field]}
        defaults = {model_field: row[col] for col, model_field in field_map.items()}
        model.objects.update_or_create(defaults=defaults, **lookup)

def run_import():
    parser = argparse.ArgumentParser(description="Import Excel data into Django ORM")
    parser.add_argument('excel_file', help="Path to the .xlsx file")
    args = parser.parse_args()
    
    excel_file = pd.ExcelFile(args.excel_file)
    
    # Sheet "Observation"
    if 'Observation' in excel_file.sheet_names:
        data_frame = excel_file.parse('Observation')
        import_sheet(
            data_frame,
            models.Group,
            key_field='feide_id',
            field_map={
                'display_name': 'display_name',
                'subject_code': 'subject_code',
                'group_subject_code': 'group_subject_code',
            }
        )
    
    # Continue for Users, Groups, UserGroups, Goals, Situations, Observations, Status, StatusGoals...
    # For relationships, you may need to look up foreign-key objects:
    # e.g. school = models.School.objects.get(feide_id=row['school_feide_id'])
    # then include school=school in defaults.
    
    print("Import complete.")

if __name__ == '__main__':
    run_import()
