# RecEval

A front end for browsing recommendation sets generated for various research projects. 
The web app is based on [Django](https://docs.djangoproject.com) and available as
[Docker image](https://hub.docker.com/r/aggipp/receval/).

## Install

```bash
# create environment
conda create -n receval python=3.7
conda activate receval

# install dependencies
pip install -r requirements.txt

# setup database (sqlite by default)
python manage.py migrate

# create admin user
python manage.py createsuperuser
```

## Commands

```bash
# load dummy data
python manage.py loaddata dummy.json

# Start dev-server
python manage.py runserver

# Start production server
gunicorn --bind 0.0.0.0:8000 receval.wsgi

# Import Citolytics dump into database
python manage.py import_cpa --input citolytics_sample.json --empty

# Collect statics (run before production deployment)
python manage.py collectstatic --noinput
```

## Environment
```
# general
export DATABASE_URL="mysql://receval:foo@localhost/receval"

# wikipedia
export RECEVAL_WIKI="en.wikipedia.org"

# zbmath
ZBMATH_DATABASE_URL=postgresql+psycopg2://postgres@...2224/postgres
ZBMATH_SSL_CERT="~/.postgresql/client.crt"
ZBMATH_SSL_KEY="~/.postgresql/client.key"
ZBMATH_SSL_ROOTCERT="~/.postgresql/root.crt"

```

## Docker

```bash
# Pull image
docker pull aggipp/receval:latest

# Build image from repo
docker build -t receval .

# Run web server on port 8000
docker run -p 8000:8000 receval

# Run unit tests within image
docker run receval python manage.py test

# Tag image for hub
docker tag receval aggipp/receval:latest  

# Push to hub
docker push aggipp/receval:latest
```

For development, running `docker-compose` is recommended:

```bash
docker-compose -f docker-compose.dev.yml up

# init database and load dummy data
docker-compose -f docker-compose.dev.yml exec app python manage.py migrate
docker-compose -f docker-compose.dev.yml exec app python manage.py loaddata dummy.json
```

## Export feedback

You can export all collected user feedback as CSV file:

```bash
python manage.py export_feedback <name> <my_output.csv> --override
```

## zbMATH

```bash
# Import recommendations (and override existing ones)
python manage.py import_zbmath data/zbmath_recommendations.csv --empty
```

## Setup SSH Tunnel to WMF Labs

Wikimedia provides an Elasticsearch cluster with enwiki index that we can use to retrieve MLT recommendations. 
However, the cluster is only reachable from within the labs network. Hence, we need to use a SSH tunnel.

```
# Create SOCKS proxy (port 1081)
ssh -fN -D localhost:1081 receval.tunnel.local

# Test proxy (ignore https)
curl --proxy socks5h://localhost:1081 https://relforge1001.eqiad.wmnet:9243 -k
```

## Data model

```
Experiment
- name
- description / welcome text

Item
- title
- external_id
- data (json)

Recommendation
- experiment
- item id
- seed id
- source
- rank
- score

Feedback
- user id
- seed item id
- recommendation item  id
- rating (likert scale)
- is_relevant (true/false/null)
- comment (text)

```

## License

MIT