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


## References

https://github.com/python-pinot-dbapi/pinot-dbapi

https://pypi.org/project/pinotdb/