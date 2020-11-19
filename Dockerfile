# start from an official image
FROM python:3.7

# arbitrary location choice: you can change the directory
RUN mkdir /app
WORKDIR /app

# copy req file first
COPY requirements.txt /app/requirements.txt

# install our dependencies
RUN pip install -r requirements.txt

# copy all other project code
COPY . /app

ENV DJANGO_SETTINGS_MODULE=receval.settings
ENV DJANGO_CONFIGURATION=Prod
ENV DATABASE_URL="sqlite:///db.sqlite3"
ENV DJANGO_SECRET_KEY=foobar12

RUN python manage.py collectstatic --no-input

# Locale
#RUN python manage.py compilemessages --l de --l en

# expose the port 8000
EXPOSE 8000

# define the default command to run when starting the container
# gunicorn --bind 0.0.0.0:8000 oldp.wsgi:application
# " --log-file", "-", "--log-level", "debug",
CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:8000", "--timeout", "1000", "receval.wsgi:application"]

