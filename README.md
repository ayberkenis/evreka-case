# Evreka Case

This case has been given by Evreka to me as a part of the recruitment process. I estimated to complete the tasks in 10-12 hours. I can tell that, I have completed both tasks in 14 hours.

## Table of Contents

- [Get Started](#get-started)
  - [Environment setup](#environment-setup)
  - [Docker Deployment](#docker-deployment)
  - [Done!](#done)
- [FAQ](#faq)
  - [Which technologies has been used?](#faq-1)
  - [Why 1 project with 2 apps instead of 2 separate projects?](#faq-2)
  - [What would I do if these was a real applications that will be deployed?](#faq-3)
  - [How did you handle high data volumes in the project?](#faq-4)
  - [Why did you choose MySQL over NoSQL databases?](#faq-5)
  - [How scalable is the app?](#faq-6)
  - [How do you ensure data integrity and fault tolerance?](#faq-7)
- [Target Case #1](#target-case-1)
  - [Task](#task)
  - [Process](#process)
    - [What I did?](#what-i-did)
  - [HTTP Requests (Python)](#http-requests-python)
    - [List Device Data / Start - End and Device Id Filters](#list-device-data--start---end-and-device-id-filters)
    - [Latest Device Data](#latest-device-data)
    - [Insert Device Data](#insert-device-data)
- [Case 2 (TCP Tracking)](#case-2-tcp-tracking)
  - [Why 1 Project with 2 Apps Instead of Separate Projects?](#why-1-project-with-2-apps-instead-of-separate-projects)
  - [Why Two Separate Tables?](#why-two-separate-tables)
  - [TCP Data Handling](#tcp-data-handling)
  - [Send Request via Python Socket](#send-request-via-python-socket)
  - [Send Request via nmap's ncat.exe (Windows)](#send-request-via-nmaps-ncatexe-windows)
- [Production](#production)
- [Testing](#testing)
  - [Grant Privileges](#grant)
  - [Undoing Privileges](#undoing)

## [Get Started](#get-started)

First, I'd like to guide you through the deployment steps.

### [**Environment setup**](#environment-setup)

> [!IMPORTANT]  
> You have to create your own .env file so ORM can create and migrate necessary tables. If you don't create the file, it's not possible for Django to serve.

You will need to create `.env` file in the root folder of the project. Below is an example of what keys are used in the environment.

```bash
# .env
MYSQL_USER=evreka_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_ROOT_PASSWORD=your_mysql_root_password
MYSQL_DB=evreka_db
MYSQL_HOST=db
MYSQL_PORT=3306
```

### [**Docker Deployment**](#docker-deployment)

You can deploy the project by running the following command. This will automatically deploy the needed frameworks, project files and libraries.

```bash
docker-compose.yml up --build
```

### [Done!](#done)

Your deployment is ready. You can visit http://localhost:8000/tracking/swagger to find out what endpoints are available.

## [**FAQ**](#faq)

1. [**Which technologies has been used?**](#faq-1)

   I have decided to use Django as the backend. My goal was to make the project scalable and flexible. As Django is a MVC framework, it made the case easier to develop and make it ready for the deployment.

   I've used MySQL as the static database for making the project simple and error-prone. When I started the project, I was thinking to use MongoDB or Apache Cassandra (NoSQL) but Celery with RabbitMQ as broker was looking promising on performance. It's still possible to use Mongo instead of MySQL but I believe MySQL with queue's can also perform more than enough for this type of data exchange.

2. [**Why 1 project with 2 apps instead of 2 separate projects?**](#faq-2)

   I have started the case with 2 separate Django projects but then I decided to have both cases as microservices of the same project as only difference between two tasks was to HTTP/TCP handling which did not require me to have separate projects for the same purpose. This made development and deployment much easier.

3. [**What would I do if these was a real applications that will be deployed?**](#faq-3)

   I'd probably wouldn't have 2 separate tables for 2 tasks as they're designed to keep identical type of data. But as nothing was mentioned in the assessment paper, I decided to have two separate tables doing the same thing except TCP was writing data in Case 2 and HTTP POST request was writing data in the Case 1.

   Also, I'd have backup Redis instance addition to RBMQ server, as datas that were written is important, I'd have caching in Redis instance.
   I haven't implemented Redis caching yet, If needed it is easy to implement and would take 2-3 hours to complete.

4. [**How did you handle high data volumes in the project?**](#faq-4)

   I leveraged RabbitMQ and Celery to process incoming data asynchronously, which allows the system to handle high traffic without overloading the database or the application. Data is stored in a MySQL database, which is optimized for structured data and supports indexing for fast query performance.

5. [**Why did you choose MySQL over NoSQL databases?**](#faq-5)

   MySQL was chosen because the data has a clear, structured format (e.g., device ID, timestamp, location, and speed). Relational databases like MySQL offer strong consistency and are well-suited for scenarios that involve filtering and querying based on structured criteria, such as specific date ranges or device IDs.

6. [**How scalable is the app?**](#faq-6)

   The system is highly scalable due to its microservices-based architecture, the use of RabbitMQ for asynchronous task handling, and Docker for containerization. Horizontal scaling can be achieved by deploying additional Celery workers and database replicas to handle higher workloads.

7. [**How do you ensure data integrity and fault tolerance?**](#faq-7)

   Data integrity is maintained by enforcing validations at the API and database level. Fault tolerance is achieved through Celery’s retry mechanism for failed tasks and RabbitMQ’s ability to store undelivered messages in a queue until they can be processed. Additionally, Docker ensures isolated environments that minimize dependency-related failures.

### [**Target Case #1**](#target-case-1)

#### [**Task**](#task):

You should be able to get location, speed, etc. location information intensively to Rest API
services (you can think of 1 million of this data per day). You can store this data in a
database of your choice. The data coming to API services should be processed
asynchronously, so you need to use a queue management tool, we currently use RabbitMQ
or Celery. We should be able to access this data for a specific date range + you should create
Rest API services where we can only access the last data for a device.

### [**Process**](#process):

#### [**What I did?**](#what-i-did)

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

### [**HTTP Requests (Python)**](#http-requests-python)

#### [**List Device Data / Start - End and Device Id Filters.**](#list-device-data--start---end-and-device-id-filters)

You can list device data, filter data by `start_date` | `end_date` | `device_id`

```py
import requests

url = "http://localhost:8000/tracking/data/list/?start_date=2024-11-11&end_date=2024-11-13&device_id=123"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
```

#### [**Latest Device Data**](#latest-device-data)

You can list latest device data for the given Id.

```py
import requests

url = "http://localhost:8000/tracking/data/latest/123"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

```

#### [**Insert Device Data**](#insert-device-data)

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

### [**Case 2 (TCP Tracking)**](#case-2-tcp-tracking)

#### [**Why 1 Project with 2 Apps Instead of Separate Projects?**](#why-1-project-with-2-apps-instead-of-separate-projects)

Initially, I considered creating two separate Django projects for the two tasks. However, I realized that combining them into one project with two apps was more efficient and aligned with the microservices approach. Here’s why:

1. **Shared Resources and Simplified Deployment:**

Both tasks required similar configurations (e.g., RabbitMQ, Celery, MySQL), so having one project allowed me to reuse these settings without duplication. This reduced complexity for both development and deployment.

2. **Logical Separation via Apps:**

Django’s app structure allowed me to maintain logical separation between the two tasks (HTTP tracking and TCP tracking) while keeping them under a single project umbrella. This approach made the codebase modular and scalable while avoiding unnecessary overhead.

3. **Microservices Structure:**

Each app acts as a self-contained microservice within the project. They have independent models, views, and configurations, enabling easy scaling or further separation into standalone services in the future if needed.

4. **Development Speed:**

Sharing a single database and RabbitMQ configuration reduced the time needed to set up and maintain the development environment, allowing me to focus on implementing features rather than managing infrastructure.

### [**Why Two Separate Tables?**](#why-two-separate-tables)

Although both apps store similar data, I created two separate tables to reflect their unique purposes and ensure flexibility for future requirements:

- The **HTTP Tracking** app stores data received via REST API, designed for high-frequency writes from HTTP POST requests.

- The **TCP Tracking** app stores data received via a TCP socket, with data being parsed and saved into its own table.

This separation avoids any potential conflicts between data sources and ensures clear data lineage, making it easier to trace and debug issues specific to one app.

### [**TCP Data Handling**](#tcp-data-handling)

The TCP Tracking app listens for data on a specified port `(localhost:9999)`. Here’s how data is sent and processed:

- TCP Server: A simple TCP server in the app listens for incoming connections and reads data.
- Celery Integration: Upon receiving data, the app sends it to a Celery task for asynchronous processing.
- Data Insertion: The processed data is stored in the tcp_tracking table.

### [You can send request via socket std lib](#you-can-send-request-via-socket-std-lib)

```python
import socket
import json

# TCP server details
TCP_IP = 'localhost'
TCP_PORT = 9999

# Sample data
data = {
    "device_id": "device123",
    "location": "123.456,78.901",
    "speed": "55.5"
}

# Serialize data to JSON
json_data = json.dumps(data)

# Open a socket connection
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((TCP_IP, TCP_PORT))  # Connect to the server
    s.sendall(json_data.encode())  # Send data
    response = s.recv(1024)  # Receive server response (if any)

# Print server response
print(f"Server response: {response.decode()}")
```

### [**You also can nmap 's ncat.exe (Windows)**](#you-also-can-nmap-s-ncatexe-windows)

Nmap should be installed and added to your PATH.

```bash
echo {"device_id": "device123", "location": "123.456,78.901", "speed": "55.5"} | ncat.exe localhost 9999
```

## [**Production**](#production)

When deploying to production environment, host should allow TCP connections from `9999` and TCP/UDP from `8000` if not behind reverse proxy.

You can simply run the composer command to build and run the case.

```bash
docker-compose up --build
```

## [**Testing**](#testing)

When testing, for security reasons you should grant **MYSQL_USER** Create Schema etc. privileges so it can create `test_{MYSQL_DATABASE}` and automatically test what's needed.

```bash
docker-compose run web python manage.py test
```

> [!CAUTION]
> You have to give the following privileges to the MYSQL_USER defined in your .env file for testing purposes. This makes testing possible as default user has no privileges to create schema's on the server. Don't forget to revoke the privileges afterwards, otherwise it will make the database vulnerable to SQL attacks.

### [**Privileges**](#grant)

```bash
docker exec -it evreka-case-db-1 mysql -u root -p
```

When prompted, enter the `MYSQL_ROOT_PASSWORD` you have defined in the .env file previously.

Then instruct MYSQL to grant the privileges, by default user is `evreka_user` you can change the SQL statement below.

```bash
GRANT CREATE, ALTER, DROP, REFERENCES, INDEX, SELECT, INSERT, UPDATE, DELETE, CREATE TEMPORARY TABLES, CREATE VIEW, SHOW VIEW, TRIGGER, CREATE ROUTINE, ALTER ROUTINE, EXECUTE ON *.* TO 'evreka_user'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

#### [**Undoing**](#undoing)

You can revoke all privileges of the user and grant default privileges again.

```bash
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'evreka_user'@'%';
FLUSH PRIVILEGES;
```

```bash
GRANT SELECT, INSERT, UPDATE, DELETE ON evreka_db.* TO 'evreka_user'@'%';
FLUSH PRIVILEGES;
```

---

Thank you for your consideration.

Best regards,

Ayberk.
