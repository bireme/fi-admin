#! coding: utf-8
from django.core.urlresolvers import reverse, reverse_lazy

from django.http import HttpResponse, HttpResponseRedirect

from django.views.generic.list import ListView
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db.models import Count
from django.db import connection

from django.conf import settings

from utils.views import ACTIONS
from utils.views import LoginRequiredView, SuperUserRequiredView
from utils.context_processors import additional_user_info

from collections import OrderedDict
from main.models import Descriptor, ThematicArea
from multimedia.models import Media, MediaCollection
from utils.views import CSVResponseMixin


class ReportsListView(LoginRequiredView, CSVResponseMixin, ListView):
    """
    Handle list view for reports
    """
    paginate_by = settings.ITEMS_PER_PAGE

    template_name = 'reports/index.html'
    context_object_name = 'report_rows'

    def dispatch(self, *args, **kwargs):
        return super(ReportsListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        source_name = self.request.GET.get('source', None)
        report = self.request.GET.get('report', None)
        filter_status = self.request.GET.get('status', None)
        filter_thematic = self.request.GET.get('filter_thematic', None)
        filter_created_by_cc = self.request.GET.get('filter_created_by_cc', None)
        export = self.request.GET.get('export', '')
        report_rows = []

        if export == 'csv':
            self.paginate_by = None

        if report and source_name:
            source_ctype = ContentType.objects.get(model=source_name)
            source = source_ctype.model_class()

            if report == '1':
                user_data = additional_user_info(self.request)
                user_list = User.objects.all()
                user_filter_list = []

                # if is superuser or is a user from BR1.1 (BIREME) 
                if self.request.user.is_superuser or user_data['user_cc'] == 'BR1.1':
                    user_filter_list = user_list
                else:
                    # else filter only users from the same CC as request.user
                    for user in user_list:
                        if not user.is_superuser:
                            user_cc = user.profile.get_attribute('cc')
                            if user_cc == user_data['user_cc']:
                                user_filter_list.append(user)

                for user in user_filter_list:
                    source_list = source.objects.filter(created_by=user)
                    if filter_status:
                        source_list = source_list.filter(status=filter_status)
                    if filter_created_by_cc:
                        source_list = source_list.filter(cooperative_center_code=filter_created_by_cc)
                    if filter_thematic:
                        source_list = source_list.filter(thematics__thematic_area=filter_thematic)

                    total_by_user = source_list.count()
                    if total_by_user > 0:
                        data = OrderedDict()
                        data['user'] = user.username
                        data['total'] = total_by_user
                        report_rows.append(data)

                    # sort the result list by total (reverse)
                    report_rows = sorted(report_rows, key=lambda k:k['total'], reverse=True)

            elif report == '2':
                source_list = source.objects.all()
                if filter_status:
                    source_list = source_list.filter(status=filter_status)
                if filter_created_by_cc:
                    source_list = source_list.filter(cooperative_center_code=filter_created_by_cc)
                if filter_thematic:
                    source_list = source_list.filter(thematics__thematic_area=filter_thematic)

                report_rows = source_list.values('cooperative_center_code').annotate(total=Count('cooperative_center_code')).order_by('-total')

            elif report == '3' or report == '4':
                if report == '3':
                    truncate_by = 'year'
                else:
                    truncate_by = 'month'

                truncate_date = connection.ops.date_trunc_sql(truncate_by, 'created_time')
                source_list = source.objects.extra({truncate_by: truncate_date})

                if filter_status:
                    source_list = source_list.filter(status=filter_status)
                if filter_created_by_cc:
                    source_list = source_list.filter(cooperative_center_code=filter_created_by_cc)
                if filter_thematic:
                    source_list = source_list.filter(thematics__thematic_area=filter_status)

                order = "-{0}".format(truncate_by)
                report_rows = source_list.values(truncate_by).annotate(total=Count('pk')).order_by(order)

            elif report == '5':
                thematic_list = ThematicArea.objects.all().order_by('name')

                for thematic in thematic_list:
                    source_list = source.objects.filter(thematics__thematic_area=thematic)
                    if filter_status:
                        source_list = source_list.filter(status=filter_status)
                    if filter_created_by_cc:
                        source_list = source_list.filter(cooperative_center_code=filter_created_by_cc)

                    total_by_thematic = source_list.count()
                    if total_by_thematic > 0:
                        data = OrderedDict()
                        data['thematic'] = thematic
                        data['total'] = total_by_thematic
                        report_rows.append(data)

                    # sort the result list by total (reverse)
                    report_rows = sorted(report_rows, key=lambda k:k['total'], reverse=True)

            elif report == '6':
                source_list = source.objects.all()
                if filter_status:
                    source_list = source_list.filter(status=filter_status)
                if filter_created_by_cc:
                    source_list = source_list.filter(cooperative_center_code=filter_created_by_cc)
                if filter_thematic:
                    source_list = source_list.filter(thematics__thematic_area=filter_thematic)

                report_rows = source_list.values('status').annotate(total=Count('status')).order_by('-total')

            if report == '7':
                collection_list = MediaCollection.objects.all().order_by('name')

                for collection in collection_list:
                    source_list = Media.objects.filter(media_collection=collection)
                    if filter_status:
                        source_list = source_list.filter(status=filter_status)
                    if filter_created_by_cc:
                        source_list = source_list.filter(cooperative_center_code=filter_created_by_cc)
                    if filter_thematic:
                        source_list = source_list.filter(thematics__thematic_area=filter_thematic)

                    total_by_collection = source_list.count()
                    if total_by_collection > 0:
                        data = OrderedDict()
                        data['collection'] = collection
                        data['total'] = total_by_collection
                        report_rows.append(data)

                    # sort the result list by total (reverse)
                    report_rows = sorted(report_rows, key=lambda k:k['total'], reverse=True)


        return report_rows

    def get_context_data(self, **kwargs):
        context = super(ReportsListView, self).get_context_data(**kwargs)
        cc_filter_list = []
        user_filter_list = []

        user_data = additional_user_info(self.request)

        report = self.request.GET.get('report', None)

        thematic_list = ThematicArea.objects.all().order_by('name')
        user_list = User.objects.filter(is_superuser=False).order_by('username')
        # mantain in user filter list only users from the same CCS (CC's in the network) as request.user
        for user in user_list:
            user_cc = user.profile.get_attribute('cc')
            if user_cc == user_data['user_cc'] or user_cc in user_data['ccs']:
                user_filter_list.append(user)

        cc_filter_list = user_data['ccs']
        # remove duplications from list
        cc_filter_list = list(set(cc_filter_list))
        cc_filter_list.sort()

        show_advaced_filters = self.request.GET.get('apply_filters', False)

        context['cc_filter_list'] = cc_filter_list
        context['user_filter_list'] = user_filter_list
        context['thematic_list'] = thematic_list
        context['show_advaced_filters'] = show_advaced_filters
        context['title'] = u'export'
        context['params'] = self.request.GET

        return context
