from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from biblioref.models import *
from biblioref.search_indexes import *

from datetime import date, timedelta
import time


class Command(BaseCommand):
    help = 'Update Solr search index (used by plugins) for all databases (excluding LILACS)'

    def index_records(self, records, index):
        total_records = records.count()
        self.stdout.write('Total records to be indexed: %s' % total_records)
        count = 0
        commit_flag = False
        for r in records:
            count = count+1
            try:
                if count == total_records:
                    commit_flag = True
                index.update_object(r, commit=commit_flag)
            except:
                self.stdout.write("Error processing record id: %s" % r.id)

            self.stdout.write("+%s" % count)


    def handle(self, *args, **options):
        start = time.time()

        LILACS_ID = 1

        ## Index Analytics
        index = ReferenceAnalyticIndex()
        records = ReferenceAnalytic.objects.filter(~Q(indexed_database=LILACS_ID))

        self.stdout.write('Indexing analytics ...')
        self.index_records(records, index)

        ## Index Sources
        index = RefereceSourceIndex()
        records = ReferenceSource.objects.filter(~Q(indexed_database=LILACS_ID))

        self.stdout.write('Indexing sources ...')
        self.index_records(records, index)

        exec_time = time.time() - start
        self.stdout.write("Execution time: %s"  % time.strftime("%H:%M:%S", time.gmtime(exec_time)))