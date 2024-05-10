from django.db import connections

def SET_PARENT(collector, field, sub_objs, using):
    parent_field = sub_objs.first().parent.parent
    for item in sub_objs:
        item.parent = parent_field
        item.save()
    
    if field.null and not connections[using].features.can_defer_constraint_checks:
        collector.add_field_update(field, None, sub_objs)
