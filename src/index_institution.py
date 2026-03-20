from institution.models import *
from institution.search_indexes import *

index = InstitutionIndex()
records = Institution.objects.all()
print 'Total records: %s' % records.count()

for r in records:
    print r.id
    index.update_object(r)
