# Python Client

## Install

```bash
pip install pinotdb
```

# Usage

## With DB-API

```python
from pinotdb import connect

conn = connect(host='localhost', port=8099, path='/query/sql', scheme='http')
curs = conn.cursor()

curs.execute("""
		SELECT 
		firstName,
		lastName,
		subject,
		score,
		TIMECONVERT(timestampInEpoch, 'MILLISECONDS', 'DAYS') AS entrySince 
		FROM transcript 
		WHERE studentID=200
	""")

for row in curs:
    print(row)
```

## With SqlAlchemy

```python
from sqlalchemy import *
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import *

# uses HTTP by default. The first port is that of the broker
engine = create_engine('pinot://localhost:8099/query/sql?controller=http://localhost:9000/') 
query = "select * from transcript where studentID=200"
result = engine.execute(query)

for row in result:
    print(row)

result.close()
````

References
==========
https://github.com/python-pinot-dbapi/pinot-dbapi

https://pypi.org/project/pinotdb/