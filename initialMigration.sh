#!/bin/sh
<<<<<<< HEAD
# rm -r "./PS2/migrations/0001_initial.py"
# rm -r "db.sqlite3"
python manage.py clearModels
# python manage.py makemigrations PS2
# python manage.py migrate
=======
rm -r "./PS2/migrations/0001_initial.py"
rm -r "db.sqlite3"
# python manage.py clearModels
python3 manage.py makemigrations PS2
python3 manage.py migrate
>>>>>>> 999f7306e1809cc460d51e36d61997ce46d8d59d
# python manage.py populateDB
exit 0