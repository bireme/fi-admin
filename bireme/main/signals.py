from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType

from django.dispatch import receiver
from django.db.models.signals import post_save

from models import Resource

@receiver(post_save, sender=Resource)
def register_action(sender, instance, signal, created, **kwargs):

    LogEntry.objects.log_action(
            user_id = instance.creator_id,
            content_type_id = ContentType.objects.get_for_model(instance).pk,
            object_id = instance.pk,
            object_repr = unicode(instance.title),
            change_message = instance.changed_fields,
            action_flag = ADDITION if created else CHANGE)


