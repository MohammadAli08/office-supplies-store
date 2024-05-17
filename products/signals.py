from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import ProductGallery


@receiver(post_delete, sender=ProductGallery)
def delete_image_on_delete(sender, instance, **kwargs):
    """
    Delete images from local filesystem when object is deleted.
    """
    storage, path = instance.image.storage, instance.image.path
    storage.delete(path)


@receiver(pre_save, sender=ProductGallery)
def delete_image_on_change(sender, instance, **kwargs):
    """
    Deletes old image from local filesystem when 
    ProductGallery object is updated with new image.
    """

    # If the instance is being created, end the process.
    if not instance.pk:
        return False
    
    # Try to get the current instance image.
    try:
        old_image = ProductGallery.objects.get(pk=instance.pk).image
    except ProductGallery.DoesNotExist:
        return False

    new_file = instance.image

    # If the image changes, delete the previous image.
    if not old_image == new_file:
        storage, path = old_image.storage, old_image.path
        storage.delete(path)
