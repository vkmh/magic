from django.db import IntegrityError

def save_or_get_existing(object_to_save):
    """Saves object and returns it and whether it was newly created.
    
    Returns object with matching values in object's OtherMeta.unique_fields.
    If not exist, creates it."""
    
    unique_fields = object_to_save.OtherMeta.unique_fields
    kwargs = {}
    for unique_field in unique_fields:
        unique_value = getattr(object_to_save, unique_field)
        kwargs[unique_field] = unique_value
    
    object_to_return = None
    created = False
    
    ## Check if already exists, and if so, just return it immediately instead of trying to create.
    ## Otherwise, we will be potentially iterating our pks with lots of unnecessary failing inserts.
    try:
        object_to_return = object_to_save.__class__.objects.get(**kwargs)
        if object_to_return:
            return object_to_return, created
    except:
        pass
    
    try:
        object_to_save.save()
        object_to_return = object_to_save
        created = True
    except IntegrityError, e:
        (error_number, error_message) = e
        if error_number != 1062:
            raise IntegrityError(e)

        object_to_return = object_to_save.__class__.objects.get(**kwargs)
    
    return object_to_return, created
