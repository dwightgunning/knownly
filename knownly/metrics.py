from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Sum, Count

truncate_date = connection.ops.date_trunc_sql('month', 'date_joined')
qs = User.objects.extra({'month':truncate_date})
report = qs.values('month').annotate(Count('pk')).order_by('month')

for m in report:
    print '%s\t%s' % (m['month'].strftime('%Y\t%b'),m['pk__count'])