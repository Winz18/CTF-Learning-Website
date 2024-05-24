import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Sections

@receiver(post_delete, sender=Sections)
def delete_section_image(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

@receiver(pre_save, sender=Sections)
def delete_old_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_instance = Sections.objects.get(pk=instance.pk)
    except Sections.DoesNotExist:
        return False

    old_image = old_instance.image
    if old_image and old_image != instance.image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)
