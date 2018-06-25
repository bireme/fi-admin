"""Add user created_by and modified_by foreign key refs to any model automatically.
   Almost entirely taken from https://github.com/Atomidata/django-audit-log/blob/master/audit_log/middleware.py"""
from django.db.models import signals
from django.utils.functional import curry
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from log.models import AuditLog

import threading
import json

# create a thread local variable to save user
_user = threading.local()
_m2mfield = threading.local()


# FIX https://djangosnippets.org/snippets/2179/
# http://stackoverflow.com/questions/862522/django-populate-user-id-when-saving-a-model/862870
class WhodidMiddleware(object):

    def process_request(self, request):
        if not request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if hasattr(request, 'user') and request.user.is_authenticated():
                _user.value = request.user
            else:
                _user.value = None

            signals.pre_save.connect(self.mark_whodid,  dispatch_uid=(self.__class__, request,), weak=False)
            signals.m2m_changed.connect(self.tracking_m2m, dispatch_uid=(self.__class__, request,), weak=False)
            signals.pre_delete.connect(self.mark_whodel,  dispatch_uid=(self.__class__, request,), weak=False)
            signals.post_save.connect(self.mark_whoadd,  dispatch_uid=(self.__class__, request,), weak=False)

    def process_response(self, request, response):
        signals.pre_save.disconnect(dispatch_uid=(self.__class__, request,))
        signals.pre_delete.disconnect(dispatch_uid=(self.__class__, request,))
        signals.m2m_changed.disconnect(dispatch_uid=(self.__class__, request,))
        signals.post_save.disconnect(dispatch_uid=(self.__class__, request,))
        return response

    def mark_whodel(self, sender, instance, **kwargs):
        user = self.get_current_user()
        # mark instance as deleted and call mark_whodid function
        instance.was_deleted = True
        self.mark_whodid(sender, instance, **kwargs)

    # necessary for track ManyToManyField changes
    def tracking_m2m(self, sender, instance, action, reverse, model, pk_set, **kwargs):

        field_name = sender._meta.model_name.split('_', 1)[1]

        if action == 'pre_clear':
            # before django clear the relation save as local thread variable the list of values of many to may field
            previous_ref = getattr(instance, field_name)
            previous_values = [unicode(i) for i in previous_ref.all()]

            setattr(_m2mfield, field_name, previous_values)

        if action == 'post_add':
            # compare list of pre-value with current values
            new_ref = getattr(instance, field_name)
            new_values = [unicode(i) for i in new_ref.all()]
            previous_values = getattr(_m2mfield, field_name)

            if new_values != previous_values:
                user = self.get_current_user()
                log_object_ct_id = ContentType.objects.get_for_model(instance).pk
                log_object_id = instance.pk
                log_repr = str(instance)

                field_change = [{'field_name': field_name, 'previous_value': previous_values,
                                'new_value': new_values}]
                field_change_json = json.dumps(field_change, encoding="utf-8", ensure_ascii=False)

                LogEntry.objects.log_action(user_id=user.id,
                                            content_type_id=log_object_ct_id,
                                            object_id=log_object_id,
                                            object_repr=log_repr,
                                            change_message=field_change_json,
                                            action_flag=CHANGE)

    def mark_whodid(self, sender, instance, **kwargs):
        user = self.get_current_user()
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
            related_model = getattr(instance, 'get_parent', False)
    
            # log if new, changed or deleted
            if new_object or has_changes or was_deleted:
                fields_change = self.get_changes_in_json(instance, new_object, was_deleted)

                if inline_model:
                    log_object_ct_id = instance.content_type.pk
                    log_object_id = instance.content_object.pk
                    log_repr = str(instance.content_object)
                elif related_model:
                    log_object_ct_id = ContentType.objects.get_for_model(instance.get_parent()).pk
                    log_object_id = instance.get_parent().pk
                    log_repr = str(instance.get_parent())
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

    def mark_whoadd(self, sender, instance, created, **kwargs):
        '''
        Update log record after save instance to add missing object_id
        '''
        user = self.get_current_user()
        if isinstance(instance, AuditLog) and created:
            # filter by log without object_id from the current user and action_flag = ADDITION
            log = LogEntry.objects.filter(object_id='None', object_repr=str(instance), action_flag=1,
                                          user_id=user.id)
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
                field_type = obj_model._meta.get_field(field_name).get_internal_type()

                if instance.id:
                    if field_type == 'ForeignKey':
                        previous_value = unicode(getattr(obj, field_name))
                    else:
                        previous_value = obj.__dict__.get(field_name)
                else:
                    previous_value = ''


                if field_type == 'ForeignKey':
                    new_value = unicode(getattr(instance, field_name))
                else:
                    new_value = instance.__dict__.get(field_name)

                # convert JSON to compare properly
                if isinstance(previous_value, basestring) and previous_value[0:2] == '[{':
                    try:
                        previous_value = json.loads(previous_value)
                    except ValueError:
                        pass

                if field_type == 'DateField':
                    if previous_value:
                        previous_value = previous_value.strftime("%d/%m/%Y")
                    if new_value:
                        new_value = new_value.strftime("%d/%m/%Y")

                if field_name not in exclude_log_fields and new_value != previous_value:
                    field_change.append({'field_name': field_name, 'previous_value': previous_value,
                                         'new_value': new_value})

        if field_change:
            field_change_json = json.dumps(field_change, encoding="utf-8", ensure_ascii=False)

        return field_change_json

    def get_current_user(self):
        if hasattr(_user, 'value'):
            return _user.value
        else:
            return None
