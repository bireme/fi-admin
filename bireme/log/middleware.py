"""Add user created_by and modified_by foreign key refs to any model automatically.
   Almost entirely taken from https://github.com/Atomidata/django-audit-log/blob/master/audit_log/middleware.py"""
from django.db.models import signals
from django.utils.functional import curry
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from log.models import AuditLog

import json


# FIX https://djangosnippets.org/snippets/2179/
# http://simionbaws.ro/programming/python-programming/django-python-programming/django-get-current-user-globally-in-the-project/
class WhodidMiddleware(object):
    def process_request(self, request):
        if not request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if hasattr(request, 'user') and request.user.is_authenticated():
                user = request.user
            else:
                user = None

            mark_whodid = curry(self.mark_whodid, user)
            mark_whodel = curry(self.mark_whodel, user)
            mark_whoadd = curry(self.mark_whoadd, user)
            signals.pre_save.connect(mark_whodid,  dispatch_uid=(self.__class__, request,), weak=False)
            signals.pre_delete.connect(mark_whodel,  dispatch_uid=(self.__class__, request,), weak=False)
            signals.post_save.connect(mark_whoadd,  dispatch_uid=(self.__class__, request,), weak=False)

    def process_response(self, request, response):
        signals.pre_save.disconnect(dispatch_uid=(self.__class__, request,))
        signals.pre_delete.disconnect(dispatch_uid=(self.__class__, request,))
        return response

    def mark_whodel(self, user, sender, instance, **kwargs):
        # mark instance as deleted and call mark_whodid function
        instance.was_deleted = True
        self.mark_whodid(user, sender, instance, **kwargs)

    def mark_whodid(self, user, sender, instance, **kwargs):

        if 'created_by' in instance._meta.get_all_field_names() and not instance.created_by:
            instance.created_by = user
            instance.created_time = timezone.now()
        else:
            if 'updated_by' in instance._meta.get_all_field_names():
                instance.updated_by = user
                instance.updated_time = timezone.now()

        # automatically add user cooperative center if present at field names and is not set
        if 'cooperative_center_code' in instance._meta.get_all_field_names() and not instance.cooperative_center_code:
            instance.cooperative_center_code = user.profile.get_attribute('cc')

        # trace and log changes
        if isinstance(instance, AuditLog):
            new_object = True if not instance.pk else False
            has_changes = getattr(instance, 'changed_fields', False)
            was_deleted = getattr(instance, 'was_deleted', False)
            inline_model = getattr(instance, 'content_object', False)

            # log if new, changed or deleted
            if new_object or has_changes or was_deleted:
                fields_change = self.get_changes_in_json(instance, new_object, was_deleted)

                if inline_model:
                    log_object_ct_id = instance.content_type.pk
                    log_object_id = instance.content_object.pk
                    log_repr = str(instance.content_object)
                else:
                    log_object_ct_id = ContentType.objects.get_for_model(instance).pk
                    log_object_id = instance.pk
                    log_repr = str(instance)

                # set default change type to CHANGE
                log_change_type = CHANGE
                # check if is not a inline model
                if not inline_model:
                    if new_object:
                        log_change_type = ADDITION
                    elif was_deleted:
                        log_change_type = DELETION

                # only create log entry for not empty change message
                if fields_change:
                    LogEntry.objects.log_action(user_id=user.id,
                                                content_type_id=log_object_ct_id,
                                                object_id=log_object_id,
                                                object_repr=log_repr,
                                                change_message=fields_change,
                                                action_flag=log_change_type)

    def mark_whoadd(self, user, sender, instance, created, **kwargs):
        '''
        Update log record after save instance to add missing object_id
        '''
        if isinstance(instance, AuditLog) and created:
            # filter by log without object_id from the current user and action_flag = ADDITION
            log = LogEntry.objects.filter(object_id='None', object_repr=str(instance), action_flag=1, user_id=user.id)
            if log:
                # get last log
                log = log[0]
                # update log with instance pk
                log.object_id = instance.id
                log.save()

    def get_changes_in_json(self, instance, new_object, was_deleted):
        field_change = []
        field_change_json = ''
        exclude_log_fields = settings.EXCLUDE_AUDITLOG_FIELDS

        obj_model = type(instance)
        obj_name = obj_model._meta.verbose_name.title()

        if new_object:
            field_change.append({'label': 'new', 'field_name': obj_name, 'previous_value': '',
                                 'new_value': unicode(instance)})
        elif was_deleted:
            field_change.append({'label': 'deleted', 'field_name': obj_name,
                                 'previous_value': unicode(instance), 'new_value': ''})
        else:
            # get previous attributes values of object
            obj = obj_model.objects.get(pk=instance.id)
            for field_name in instance.changed_fields:
                if instance.id:
                    previous_value = obj.__dict__.get(field_name)
                else:
                    previous_value = ''

                new_value = instance.__dict__.get(field_name)

                # convert JSON to compare properly
                if isinstance(previous_value, basestring) and previous_value[0:2] == '[{':
                    try:
                        previous_value = json.loads(previous_value)
                    except ValueError:
                        pass

                if field_name not in exclude_log_fields and new_value != previous_value:
                    field_change.append({'field_name': field_name, 'previous_value': previous_value,
                                         'new_value': new_value})

        if field_change:
            field_change_json = json.dumps(field_change, encoding="utf-8", ensure_ascii=False)

        return field_change_json
