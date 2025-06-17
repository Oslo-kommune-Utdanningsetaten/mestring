import os
import sys
from dotenv import load_dotenv
import django

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
load_dotenv(os.path.join(project_root, '.env'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

# Import models after django.setup()
from mastery.models import Goal, MasterySchema

def update_goal_mastery_schema_ids():
    print("Updating Goal mastery_schema_id to a specific MasterySchema...")
    
    # Replace with the actual ID you want to use
    target_schema_id = 'jnpaZD38MKIY'
    
    # Verify the schema exists
    try:
        schema = MasterySchema.objects.get(id=target_schema_id)
    except MasterySchema.DoesNotExist:
        print(f"Warning: MasterySchema with id '{target_schema_id}' does not exist")
        return
    
    # for each goal, set the mastery_schema_id to the target schema
    goals = Goal.objects.all()
    for goal in goals:
        if goal.mastery_schema_id is None:
            print(f"Updating Goal {goal.id} mastery_schema_id to {target_schema_id}")
            goal.mastery_schema = schema
            goal.save()
        else:
            print(f"Goal {goal.id} already has a mastery_schema_id set, skipping.")

if __name__ == "__main__":
    update_goal_mastery_schema_ids()