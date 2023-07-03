from django.core.management.base import BaseCommand

from biblioref.models import *
from biblioref.search_indexes import *

from datetime import date, timedelta
import time


class Command(BaseCommand):
    help = 'Update Solr search index (used by plugins)'


    def add_arguments(self, parser):
        parser.add_argument('--database_code', help="Informe the ID of dabase for update")
        parser.add_argument('--updated_after_date', help="Only index records updates after this date. Ex. 2023-07-01")
        parser.add_argument('--updated_after_days', help="Only index records updates after N days from current date. Ex. 7 (get records from last week)")


    def handle(self, *args, **options):
        start = time.time()

        index = ReferenceAnalyticIndex()
        records = ReferenceAnalytic.objects.all()
        filter_db = options.get('database_code')
        updated_after_date = options.get('updated_after_date')
        updated_after_days = options.get('updated_after_days')

        if filter_db:
            records = records.filter(indexed_database=filter_db)
            self.stdout.write('Database code to be indexed: %s' % filter_db)

        if updated_after_days:
            current_date = date.today()
            updated_after_date = current_date - timedelta(days=int(updated_after_days))


        if updated_after_date:
            self.stdout.write('Only index records updated after: %s' % updated_after_date)
            records = records.filter(updated_time__gte=updated_after_date)


        self.stdout.write('Total analytics records to be indexed: %s' % records.count())
        count = 0
        for r in records:
            try:
                index.update_object(r)
            except:
                self.stdout.write("Error processing record id: %s" % r.id)

            count = count+1
            self.stdout.write("+%s" % count )

        index = RefereceSourceIndex()
        records = ReferenceSource.objects.all()

        if filter_db:
            records = records.filter(indexed_database=filter_db)

        if updated_after_date:
            records = records.filter(updated_time__gte=updated_after_date)
            self.stdout.write('Only index records updated after: %s' % updated_after_date)


        self.stdout.write('Total source records to be indexed: %s' % records.count())
        count = 0
        for r in records:
            try:
                index.update_object(r)
                self.stdout.write(r.id)
            except:
                self.stdout.write("Error processing record id: %s" % r.id)

            count = count+1
            self.stdout.write("+%s" % count )

        exec_time = time.time() - start
        self.stdout.write("Execution time: %s"  % time.strftime("%H:%M:%S", time.gmtime(exec_time)))