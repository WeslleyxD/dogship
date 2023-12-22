import json
from decimal import Decimal

data = {'valor': Decimal('123.45')}


print (json.dumps(data, skipkeys=True, ensure_ascii=False, default=str))