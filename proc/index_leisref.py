from leisref.models import *
from leisref.search_indexes import *

index_db = 2


index = LeisRefIndex()
#records = Act.objects.filter(indexed_database=index_db)
records = Act.objects.all()
print 'Total records: %s' % records.count()

for r in records: 
    print r.id
    index.update_object(r)

