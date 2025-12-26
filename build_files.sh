python3 -m pip install -r requirements.txt
python3 manage.py make_migrations
python3 manage.py migrate
python3 manage.py collectstatic --noinput
