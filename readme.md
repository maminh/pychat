# PyChat Project

### running project

for sse connections redis is needed:

```bash
sudo apt install redis-server
```



create a local_params.py in root directory: with following variables:

```python
DB_HOST = 'db host'
DB_NAME = 'db name'
DB_USER = 'db user'
DB_PASS = 'db pass'

REDIS_URL = 'redis url'

DEBUG_MODE = True or False
HOST = 'server running host'
```

mysql used for database.

for creating models:

```python
from app.models import *


User.create_table()
Contact.create_table()
```

run the server using start.py