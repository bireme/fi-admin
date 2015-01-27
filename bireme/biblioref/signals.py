from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType

from django.dispatch import receiver
from django.db.models.signals import post_save

from models import Reference

# Add entry to default django log table (logentry) the create/update of a event via FI-Admin interface
@receiver(post_save, sender=Reference)
def register_action(sender, instance, signal, created, **kwargs):

    # Avoid log of first import data (old system data migration)
    if instance.created_by_id or instance.updated_by_id:
        LogEntry.objects.log_action(
            user_id = instance.created_by_id if created else instance.updated_by_id ,
            content_type_id = ContentType.objects.get_for_model(instance).pk,
            object_id = instance.pk,
            object_repr = unicode(instance),
            #change_message = instance.changed_fields,
            action_flag = ADDITION if created else CHANGE)



