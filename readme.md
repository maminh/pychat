# PyChat Project

### running project

for sse connections redis is needed:

```bash
sudo apt install redis-server
```

create a virtual environment and install project's requirements using:

```bash
pip install -r requirements.txt
```

__python version 3 should use!__

create a local_params.py in root directory with following variables:

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



### using project

first create a account.

add a contact of user you want to call then make the call using make call button.



### project code explanation

the flask framework is used for writing the web application and for SEE connections, flask_sse used.

when the index page loaded an SSE connection created using this:

```javascript
var source = new EventSource("{{ url_for('sse.stream', channel=user.username) }}");
```

every user has its own channel in the SSE stream and all of the messages associated with the user are sent using this channel.
in EventSource creation the __channel__ parameter used for this purpose.

