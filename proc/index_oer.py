from oer.models import *
from oer.search_indexes import *


index = OERIndex()
records = OER.objects.all()
#records = OER.objects.filter(pk=842)
print 'Total records: %s' % records.count()

for r in records: 
    print r.id
    index.update_object(r)

