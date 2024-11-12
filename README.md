## Evreka Case

### Target Case #1

#### Task:

You should be able to get location, speed, etc. location information intensively to Rest API
services (you can think of 1 million of this data per day). You can store this data in a
database of your choice. The data coming to API services should be processed
asynchronously, so you need to use a queue management tool, we currently use RabbitMQ
or Celery. We should be able to access this data for a specific date range + you should create
Rest API services where we can only access the last data for a device.

### Process:

#### What I did?

I have started by creating a virtual environment for the project to manage dependencies separately from other projects on my system.

```bash
python3 -m venv venv
source venv/bin/activate # venv/Scripts/activate for Windows.
```

Next, I initialized a Git repository in the project directory to track my changes and maintain a history of my commits.

```bash
git init
```

I chose to use Django as the web framework, as I thought scalability is the most cruicial idea behind this API. Installed the dependencies with following bash command.

I installed the required dependencies, including Django REST Framework for building RESTful APIs, Celery for asynchronous task processing, django-celery-results to store Celery task results in the database, and MySQL client libraries.

```bash
pip install django djangorestframework celery django-celery-results mysqlclient
```

I created a new Django project named evreka_case1 and an app called tracking to handle the tracking functionalities.

```bash
django-admin startproject evreka_case1 .
python manage.py startapp tracking
```

I have set all the configuration parameters in settings.py and decided to use .env variables.

Example .env file is given below.

```bash
# .env
MYSQL_USER=evreka_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=evreka_db
MYSQL_HOST=db
MYSQL_PORT=3306
```

I configured RabbitMQ as the message broker for Celery by adding it to the docker-compose.yml file and ensuring the Django settings point to the correct broker URL.

I wrote the DeviceData model in tracking/models.py to represent the incoming data (device ID, location, speed, etc.):

I set up docker-compose.yml to orchestrate the multiple services: the Django web app, Celery worker, RabbitMQ, and MySQL database.

Finally, I set up `drf_yasg` package to have both swagger and redoc versions of the API documentation which will be accesible at `http://localhost:8000/swagger` & `http://localhost:8000/redoc`

### HTTP Requests (Python)

#### List Device Data / Start - End and Device Id Filters.

You can list device data, filter data by `start_date` | `end_date` | `device_id`

```py
import requests

url = "http://localhost:8000/tracking/data/list/?start_date=2024-11-11&end_date=2024-11-13&device_id=123"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
```

#### Latest Device Data

You can list latest device data for the given Id.

```py
import requests

url = "http://localhost:8000/tracking/data/latest/123"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

```

#### Insert Device Data

Inserts device data using rabbitmq as broker and celery for managing queue.
Endpoint accepts, both single dictionary or list of dictionaries.

```py
import requests
import json

url = "http://localhost:8000/tracking/data/"

payload = json.dumps({
  "device_id": "123",
  "location": "Antalya",
  "speed": 60
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
```

### Case 2 (TCP Tracking)

First, I wanted to have 2 different projects for each case but I decided to have 2 seperate apps in single Django project to simplify the process for my developer experience and other developer's deployment process.
