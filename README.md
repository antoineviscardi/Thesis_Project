# Graduate Attribute Management System (GAMS)

## Prerequisite
```
pip 9.0.1
Python 3.5.2
Django 2.0.1
MySQL 1.3.12
XlsWriter 1.0.2
```

## Starting the server
A small python server can be started using the following commands.
Entering the virtual environment:
```
cd gams
source bin/activate
```
Starting the server:
```
python manage.py runserver
```

## Configuration
Django's configurations can be found in the file `~/gams/gams/settings.py`. The file is well documented but here is a description of the most important parts.

### `DATABASES` (l. 82)
The `DATABASES` variable defines the information needed by Django to connect to the database. If another database was to be used, this is the only part that would have to be adjusted.

### `EMAIL` (l.95)
The different varibales defined in that part contains the information needed by django to connect to an email service. If another email service was to be used, this is the only part that would need to be adjusted. 

## MySQL
Django is connected to a MySQL service running on the machine. The database can be manually accessed through the command line.
```
mysql -u root -p
gams1234
use gams_db
```


