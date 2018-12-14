# PyChat Project

before running project create a local_params.py in root directory:

```python
DB_HOST = 'db host'
DB_NAME = 'db name'
DB_USER = 'db user'
DB_PASS = 'db pass'
```

mysql used for database.

for creating models:

```python
from app.models import *


User.create_table()
Contact.create_table()
```

run the server using start.py