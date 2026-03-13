# Video Game Publisher Analytics API

A RESTful API for analysing video game publisher performance using a [historical sales dataset](https://www.datacamp.com/datalab/datasets/dataset-r-video-games-sales).

The system allows authenticated users to create **custom dashboards** containing  the following analytics widgets:

-   Publisher Overview
-   Publisher 'Hit Rate'
-   Publisher Efficiency
-   Publisher Regional Bias
-   Publisher Momentum
-   Publisher Comparison

Dashboards dynamically render analytics results based on stored widget configuration.

## API Documentation

A pdf version of the auto-generated API documentation is available here:

[API Docs (PDF)](docs/api-docs.pdf)

## Generative AI Chat Logs

JSON files containing extracted chat logs are available here:

["GenAI Creative Solutions"](docs/GenAI-Creative-Solutions-chat-log.json)  
["API Project Ideas"](docs/API-Project-Ideas-chat-log.json)  
["Web Services CW"](docs/Web-Services-CW-chat-log.json)  



------------------------------------------------------------------------

# Running the Project

## Uber-quick Start via Render hosted URL

    https://webservicescoursework.onrender.com/docs

If the application has not recently been running, there may be a small 'cold start' delay upon instantiation.

## Quick Start via Docker (Recommended for local deployment)

Note: terminal commands have only been tested for validity within PowerShell

### 1. Download and install Git:
https://git-scm.com/install/

Confirm that Git has sucessfully installed:
    git --version

### 2. Download and install Docker Desktop:
https://www.docker.com/products/docker-desktop

Confirm that Docker and Docker Compose have sucessfully installed:
    docker --version
    docker compose version

### 3. Clone the repository:

    git clone https://github.com/MatthewToon/WebServicesCoursework
    cd <repository filepath>

### 4. Start the application:

    docker-compose up --build

Docker will:

-   Build the FastAPI container
-   Start the PostgreSQL database
-   Install Python dependencies
-   Configure the database
-   Run database migrations
-   Launch the API server

### 5. Open the API documentation:
http://127.0.0.1:8000/docs

This opens the Swagger API interface, where the system can be tested

------------------------------------------------------------------------

# Manual Setup (Windows)

Note: terminal commands have only been tested for validity within PowerShell

## 1. Download and install Git:
https://git-scm.com/install/

Confirm that Git has sucessfully installed:
    git --version

## 2. Download and install Python (version 3.10 or newer):
https://www.python.org/downloads/windows/

NOTE: ensure **Add Python to PATH** is enabled.

Verify installation:

    python --version


## 3. Download and install PostgreSQL

Download PostgreSQL:
https://www.postgresql.org/download/windows/

During installation:

-   Create and make a note of the username and password for the `postgres` user
-   Use the default port `5432`

Create the database:

    CREATE DATABASE vgsales;


## 4. Clone the repository

    git clone https://github.com/MatthewToon/WebServicesCoursework
    cd .../WebServicesCoursework

## 5. Create Python virtual environment

    python -m venv .venv

Activate:

    .venv\Scripts\Activate.ps1

If PowerShell blocks the script, run this first:

    .\.venv\Scripts\Activate.ps1

Then retry the Activate script above.
If successful, '(.venv)' should prefix the terminal prompt: 

    (.venv) PS C:\Users\You\ ...


## 5. Install Python dependencies

    pip install -r requirements.txt

This installs all required packages, including FastAPI, SQLAlchemy, ALembic, Uvicorn, and JWT authentication libraries


## 6. Configure Environment Variables

For the sake of this assignment, the .env has been omitted from the gitignore file, so should be included when cloning the repository.

If this is not the case, create a text file in the root folder (/WebServicesCoursework), named .env, then populate it with the following:

    DATABASE_URL=postgresql+psycopg://app_user:password@localhost:5432/vgsales_api
    JWT_SECRET_KEY=supersecretkey
    JWT_ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=60


Replace `password` with your PostgreSQL password.


## 7. Create the database user

Open SQL Shell (psql) as the postgres user that was created earlier, and run:

    CREATE USER app_user WITH PASSWORD 'your.password.here';
    GRANT ALL PRIVELEGES ON DATABASE vgsales_api TO app_user;


## 8. Run database migrations

From the project root, with the virtual envrionment (.venv) still active, run:

    alembic upgrade head

If this step fails, double-check:
    - PostgreSQL is running
    - The database exists
    - The .env values are correct


## 9. Import the Dataset

Populate the database from the included dataset (vgsales.csv):

    python scripts/import_vgsales.py

Note: terminal commands have only been tested for validity within PowerShell


## 10. Start the API server

Run:

    uvicorn app.main:app --reload

If successful, you should see output similar to: 

    Uvicorn running on http://127.0.0.1:8000

Leave this terminal open while using the API


## 11. Open the API documentation

In your favourite web browser (only tested in Chrome and Edge), enter the URL:

    http://127.0.0.1:800/docs

This opens the interactive Swagger UI, where the API can be tested.

## 12. Recommended Checks

Once the server is running, test these endpoints first in Swagger 

    GET /health

Expected result: 200 OK

    GET /db-check

Expected result: 200 OK

If /health works but /db-check fails, the API is running but cannot connect to PostgreSQL.

------------------------------------------------------------------------

# Example Usage

## 1. Register user

    POST /auth/register

Example request body:

    {
      "email": "test@example.com",
      "password": "password123"
    }

Expected result: 201 Created


## 2. Login

    POST /auth/token

Log in with the same credentials as above.
Expected result: 200 OK, and response includes a JWT token

Use the returned token via the **Authorize** button in Swagger.


## 3. Authorise

Click the green 'Authorize' button in the upper-right of the API documentation page, and enter the username and password.

## 4. Create a dashboard

    POST /dashboards

Example request body:

    {
      "name": "Test Dashboard"
    }

Expected result: 201 Created

Take a note of the dashboard ID


## 5. Add widget to dashboard

    POST /dashboards/{dashboard_id}/widgets

Example request body:

    {
      "params": {
        "type": "publisher_overview",
        "publisher_slug": "nintendo",
        "from_year": 2000,
        "to_year": 2020
      }
    }

Expected result: 201 Created


## 6. Render the dashboard

    GET /dashboards/{dashboard_id}/render

Expected result:

    200 OK
    JSON response containing widget results

This confirms the full system is operational:
    1. Authentication
    2. Dashboard CRUD
    3. Widget creation
    4. Analytics execution
    5. Renderer integration

------------------------------------------------------------------------

# All Analytics Endpoints

    GET /analytics/publisher-overview\
    GET /analytics/publisher-hit-rate\
    GET /analytics/publisher-efficiency\
    GET /analytics/publisher-regional-bias\
    GET /analytics/publisher-momentum\
    GET /analytics/publisher-comparison


# Dataset Details

The dataset contains:

-   Game titles
-   Publishers
-   Platforms
-   Genres
-   NA / EU / JP / Other regional sales
-   Global sales

------------------------------------------------------------------------

# Troubleshooting

### Port already in use

If you are running something else which is bound to port 8000:

    uvicorn app.main:app --reload --port 8001

### Database connection issues

Ensure PostgreSQL is running and the `.env` file is configured
correctly.

### Missing dependencies

    pip install -r requirements.txt

------------------------------------------------------------------------

# Authors

ChatGPT and Matthew Toon
