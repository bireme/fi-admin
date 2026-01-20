#! coding: utf-8
from django.urls import reverse, reverse_lazy

from django.http import HttpResponse, HttpResponseRedirect

from django.views.generic.list import ListView
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.db import connection

from django.conf import settings

from utils.views import LoginRequiredView, SuperUserRequiredView
from utils.context_processors import additional_user_info

from collections import OrderedDict
from main.models import Descriptor, ThematicArea
from multimedia.models import Media, MediaCollection
from title.models import Title, IndexRange, IndexCode
from utils.views import CSVResponseMixin
from biblioref.models import ReferenceAnalytic

from datetime import datetime

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
        filter_year = self.request.GET.get('filter_year', None)
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

                if filter_created_by_cc:
                    # if filter by CC is set, filter only users from that CC
                    for user in user_list:
                        user_cc = user.profile.get_attribute('cc')
                        if user_cc == filter_created_by_cc:
                            user_filter_list.append(user)
                else:
                    # if no filter by CC, filter by user's CCs or all if BR1.1
                    if user_data['user_cc'] == 'BR1.1':
                        user_filter_list = user_list
                    else:
                        for user in user_list:
                            user_cc = user.profile.get_attribute('cc')
                            if user_cc == user_data['user_cc']:
                                user_filter_list.append(user)

                # Build base queryset with all filters except user (moved outside the loop)
                base_qs = source.objects.all()

                if filter_status:
                    base_qs = base_qs.filter(status=filter_status)
                if filter_thematic:
                    base_qs = base_qs.filter(thematics__thematic_area=filter_thematic)

                for user in user_filter_list:
                    # Count created objects
                    if filter_year:
                        created_count = base_qs.filter(created_by=user, created_time__year=filter_year).count()
                    else:
                        created_count = base_qs.filter(created_by=user).count()

                    # Count updated objects (excluding those already counted as created)
                    if filter_year:
                        updated_count = base_qs.filter(updated_by=user, updated_time__year=filter_year).exclude(created_by=user).count()
                    else:
                        updated_count = base_qs.filter(updated_by=user).exclude(created_by=user).count()

                    user_count = created_count + updated_count
                    if user_count > 0:
                        data = OrderedDict()
                        data['user'] = user.username
                        data['total_created'] = created_count
                        data['total_updated'] = updated_count
                        data['total'] = user_count
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

            if report == '8':
                report_rows = OrderedDict()
                # get LILACS pk for filter in Title table
                lilacs_code = IndexCode.objects.get(code='LL').pk
                # filter by LILACS indexed titles
                serial_list = Title.objects.filter(indexrange__index_code=lilacs_code).order_by('country', 'shortened_title')
                # exclude titles that doesn't have indexer_cc_code
                serial_list = serial_list.exclude(indexer_cc_code='', indexrange__indexer_cc_code='')

                report_rows = serial_list.values('shortened_title', 'indexer_cc_code', 'editor_cc_code', 'country__name', 'issn')

            # LILACS-Express by Serial
            if report == '9':
                # filter by status LILACS-Express
                llxp_list = ReferenceAnalytic.objects.filter(status=0)

                # summarize by serial
                report_rows = llxp_list.values('source__title_serial').annotate(num_pending=Count('pk')).order_by('-num_pending')

                # add information of indexer cc code
                lilacs_code = IndexCode.objects.get(code='LL').pk
                for row in report_rows:
                    indexer_cc = ''
                    current_title = row['source__title_serial']
                    title_obj = Title.objects.filter(shortened_title=current_title).first()

                    indexrange =  IndexRange.objects.filter(title=title_obj, index_code=lilacs_code)
                    if indexrange:
                        indexer_cc = indexrange[0].indexer_cc_code

                    row.update({'indexer_cc': indexer_cc})

            if report == '10':
                report_rows = OrderedDict()
                serial_list = Title.objects.all().order_by('status')
                report_rows = serial_list.values('shortened_title', 'status', 'issn', 'country__name')

        return report_rows

    def get_context_data(self, **kwargs):
        context = super(ReportsListView, self).get_context_data(**kwargs)
        cc_filter_list = []
        user_filter_list = []
        thematic_list = []
        current_year = datetime.now().year
        year_list = [current_year - i for i in range(5)]

        user_data = additional_user_info(self.request)

        report = self.request.GET.get('report', None)

        thematic_list = ThematicArea.objects.all().order_by('name')
        cc_filter_list = user_data['ccs']

        if type(cc_filter_list) == list:
            # sort list
            cc_filter_list.sort()

        show_advaced_filters = self.request.GET.get('apply_filters', False)

        context['cc_filter_list'] = cc_filter_list
        context['thematic_list'] = thematic_list
        context['year_list'] = year_list
        context['show_advaced_filters'] = show_advaced_filters
        context['title'] = u'export'
        context['params'] = self.request.GET

        return context
