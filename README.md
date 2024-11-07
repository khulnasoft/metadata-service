![pylint](https://img.shields.io/badge/pylint-10.00-darkred?logo=python&logoColor=white) 


# Metatdata Service

### Table of Contents
1. [Run Locally](#Run Locally)
2. [Run via Docker](#Run via Docker)


## Run Locally

1. Create an empty PostgreSQL database and update the `settings.dev-localhost.toml` file with the database details.
2. Create a virtual environment and install the dependencies.
3. Run `main.py` (a database schema will be generated in your database).
4. View the API Swagger at: [http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs).

## Run via Docker

1. From the `metadata_service` directory, run:
   ```sh
   docker build --no-cache -t metadata_service_img .

2. Run the container with:
    ```sh
    docker run -p 8000:8000 metadata_service_img

### Running with docker-compose

- Make sure you're running docker-compose v2
```shell
docker compose version
```
- Build docker image locally: `docker build -t metadata-svc:latest .`
- Update postgres connection string to `"postgresql://postgres:postgres@db:5432/postgres"`
- Run docker-compose: `docker compose up`
- You should see output similar to:
```
[+] Running 2/2
 ✔ Container metadata-service-db-1        Created                                                                                                                                                                                 0.0s 
 ✔ Container metadata-service-metadata-1  Recreated                                                                                                                                                                               0.1s 
Attaching to db-1, metadata-1
db-1        | 
db-1        | PostgreSQL Database directory appears to contain a database; Skipping initialization
db-1        | 
db-1        | 2024-09-10 14:15:13.540 UTC [1] LOG:  starting PostgreSQL 14.1 on x86_64-pc-linux-musl, compiled by gcc (Alpine 10.3.1_git20211027) 10.3.1 20211027, 64-bit
db-1        | 2024-09-10 14:15:13.540 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
db-1        | 2024-09-10 14:15:13.540 UTC [1] LOG:  listening on IPv6 address "::", port 5432
db-1        | 2024-09-10 14:15:13.549 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
db-1        | 2024-09-10 14:15:13.560 UTC [21] LOG:  database system was interrupted; last known up at 2024-09-10 14:12:23 UTC
db-1        | 2024-09-10 14:15:13.699 UTC [21] LOG:  database system was not properly shut down; automatic recovery in progress
db-1        | 2024-09-10 14:15:13.704 UTC [21] LOG:  redo starts at 0/16FAAB8
db-1        | 2024-09-10 14:15:13.704 UTC [21] LOG:  invalid record length at 0/16FAAF0: wanted 24, got 0
db-1        | 2024-09-10 14:15:13.704 UTC [21] LOG:  redo done at 0/16FAAB8 system usage: CPU: user: 0.00 s, system: 0.00 s, elapsed: 0.00 s
db-1        | 2024-09-10 14:15:13.736 UTC [1] LOG:  database system is ready to accept connections
metadata-1  | 2024-09-10 14:15:18.075 | INFO     | __main__:<module>:52 - Running main info
metadata-1  | 2024-09-10 14:15:18.076 | DEBUG    | __main__:<module>:53 - Running main debug
metadata-1  | 2024-09-10 14:15:18.166 | INFO     | __main__:run_alembic_upgrade:43 - Running Alembic upgrade
metadata-1  | 2024-09-10 14:15:18.169 | DEBUG    | env_py:run_migrations_online:50 - running Migration ONLINE
metadata-1  | 2024-09-10 14:15:18.308 | INFO     | 2024_09_03_1445_261fa6af3627_initial_schema_py:upgrade:24 - Creating initial schema
metadata-1  | 2024-09-10 14:15:18.425 | INFO     | __main__:run_alembic_upgrade:45 - Alembic upgrade completed successfully
metadata-1  | INFO:     Started server process [1]
metadata-1  | INFO:     Waiting for application startup.
metadata-1  | INFO:     Application startup complete.
metadata-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

#### Database state retention:
The DB created by docker compose will retain values on recreation.
To remove the DB and start fresh, run:
```sh
docker volume rm metadata_db
```

## Makefile
In the makefile, you will find commands that will help you during development

to run tests, run:
```sh
make test
```

to run linter, formatter and tests, run:
```sh
make perfect
```

allway run this before pushing, as build will fail for 
* failing tests
* coverage lower then 61%
* formatting issues
* linting issues

## 
## Deploying to development

To deploy to development, run the github action: "Build and push Metadata service for dev cluster"


To use the development env deployment during development or access it via browser
define the following port forwarding:
```sh
kubectl port-forward svc/metadata-service 8000:8000 -n metadata-service
```
You should be able to access:  `http://localhost:8000/docs`

If this doesn't work, please do:

1. check with Ori you have k8s permission
2. configure kubectl:
```sh
gcloud container clusters get-credentials development-cluster --region us-central1 --project khulnasoft-development
```
This will add the cluster to your ~/.kube/config

You can use
```sh
kubectl config get-contexts
```
to see for which cluster kubectl is configured. Verify you can access the cluster using
```shell
kubectl version
```
I recommend to install Lens as a k8s IDE, it will make your life easier, won’t need to remember the port-forward kubectl syntax..

## Working with Alembic to manade database migrations
Whenever you make changes to the database schema, 
you need to create a databse revision script.
On service startup, alembic will update the db to the latest revision, by running all the revision scripts in order.

### Creating a schema revision

1. create a new revision
    ```sh
    alembic revision -m "create account table"
    ```
   This will generate a new script in migrations directory.
   Implement the upgrade and downgrade functions in the script.

### Other Alembic commands

2. generate revision script
    ```sh
    alembic revision --autogenerate -m "your db change description"
    ```
2. upgrade database
    ```sh
    alembic upgrade head
    ```
3. downgrade database
    ```sh
    alembic downgrade -1
    ```