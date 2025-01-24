# Metadata Catalogue API 

!!! note
    
    This page was the old readme. Re-organizing and updating it into our structured documentation
    pages is work in progress. This page will serve as an overview page that serves as a 
    "getting started" page and quick reference, with references to pages with in-depth information.

This repository contains the AI on Demand (AIoD) REST API. It is built with 
[FastAPI](https://fastapi.tiangolo.com/)
that interacts with a database ([MySQL](https://hub.docker.com/_/mysql))
and [OpenML's REST API](https://www.openml.org/apis).
Both the database and the REST API are run from docker in separate containers.

The AIoD REST API will allow any kind of service to interact with the AIoD portal to discover, 
retrieve, and share AI resources. It forms the connection between user-facing components, such 
as the AIoD website or Python Client API, and the backend. The metadata for datasets, models 
and other resources can be accessed, added, updated and deleted through this API. 

## Architecture
All metadata is stored in the AIoD metadata database. For every instance of the API (there will 
be multiple running instances, for reliability and performance), an instance of this database 
will run on the same machine (on the same node). The type of database is not yet determined, for 
now we use a simple MySQL database.

The metadata is stored in AIoD format. When the user requests an item, such as a dataset, it can 
be returned in AIoD format, or converted to any supported format, as requested by the user. For 
datasets, we will for instance support schema.org and DCAT-AP.

Requesting a dataset will therefore be simply:

![Get dataset UML](../media/GetDatasetUML.png)

To fill the database, a synchronization process must be running continuously for every platform 
(e.g. HuggingFace or OpenML). This synchronization service of a platform will be deployed at a 
single node. The synchronization service queries its platform for updates, converts the metadata 
to the AIoD format and updates the database.

Note that this synchronization process between the platform and the database, is different from 
the synchronization between database instances. The latter is under discussion in the AIoD 
Synchronization Meetings. 


## Prerequisites
- Linux/MacOS/Windows (should all work)
- [Docker](https://docs.docker.com/get-docker/) 
- [Docker Compose](https://docs.docker.com/compose/install/) version 2.21.0 or higher

For development:
- `Python3.11` with `python3.11-dev` (`sudo apt install python3.11-dev` on Debian)
- Additional 'mysqlclient' dependencies. Please have a look at [their installation instructions](https://github.com/PyMySQL/mysqlclient#install).

## Production environment

For production environments elasticsearch recommends -Xss4G and -Xmx8G for the JVM settings.\
This parameters can be defined in the .env file.
See the [elasticsearch guide](https://www.elastic.co/guide/en/logstash/current/jvm-settings.html).

For Keycloak, the `--http-enabled=true` and `--hostname-strict-https=false` should be omitted 
from the docker-compose file.

## Installation

This repository contains two systems; the database and the REST API.
As a database we use a containerized MySQL server (through Docker), the REST API can be run locally or containerized.
Information on how to install Docker is found in [their documentation](https://docs.docker.com/desktop/).

### Using docker compose
```bash
docker compose --profile examples up -d
```

starts the MYSQL Server, the REST API, Keycloak for Identity and access management and Nginx for reverse proxying. \
Once started, you should be able to visit the REST API server at: http://localhost and Keycloak at http://localhost/aiod-auth \
To authenticate to the REST API swagger interface the predefined user is: user, and password: password \
To authenticate as admin to Keycloak the predefined user is: admin and password: password \
To use a different DNS hostname, refer to the ["Changing the configuration"](#changing-the-configuration) section below for instructions on how to ovverride `HOSTNAME` in `.env` and `opendid_connect_url` in `config.toml`. \
This configuration is intended for development, DO NOT use it in production. 

To turn if off again, use 
```bash
docker compose --profile examples down
```

To connect to the database use `./scripts/database-connect.sql`.

```bash
mysql> SHOW DATABASES;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
4 rows in set (0.03 sec)
```

Now, you can visit the server from your browser at `localhost:8000/docs`.


### Changing the configuration
You may need to change the configuration locally, for example if you want different ports to be used.
Do not change files, instead add overrides.

#### Docker Compose
For docker compose, the environment variables are defined in the `.env` file. 
To override variables, for example `AIOD_LOGSTASH_PORT`, add a new file called `override.env`:
```bash {title='override.env'}
AIOD_LOGSTASH_PORT=5001
```
Then also specify this when you invoke docker compose, e.g.:
`docker compose --env-file=.env --env-file=override.env up`
Note that **order is important**, later environment files will override earlier ones.
You may also use the `./scripts/up.sh` script to achieve this (see ["Shorthands"](#shorthands) below).

#### Config.toml
The main application supports configuration options through a `toml` file.
The defaults can be found at `src/config.default.toml`.
To override them, add a `src/config.override.toml` file.
It follows the same structure as the default file, but you only need to specify the variables to override.

#### Using connectors
You can specify different connectors using

```bash
docker compose --profile examples --profile huggingface-datasets --profile openml --profile zenodo-datasets up -d
docker compose --profile examples --profile huggingface-datasets --profile openml --profile zenodo-datasets down
```

Make sure you use the same profile for `up` and `down`, or use `./scripts/down.sh` (see below),
otherwise some containers might keep running.

### Shorthands
We provide two auxiliary scripts for launching docker containers and bringing them down.
The first, `./scripts/up.sh` invokes `docker compose up -d` and takes any number of profiles to launch as parameters.
It will also ensure that the changes of the configurations (see above) are observed.
If `USE_LOCAL_DEV` is set to `true` (e.g., in `override.env`) then your local source code will be mounted on the containers,
this is useful for local development but should not be used in production.
E.g., with `USE_LOCAL_DEV` set to `true`, `./scripts/up.sh` resolves to:
`docker compose --env-file=.env --env-file=override.env -f docker-compose.yaml -f docker-compose.dev.yaml --profile examples  up -d`

The second script is a convenience for bringing down all services, including all profiles: `./scripts/down.sh`

#### Local Installation

If you want to run the server locally, you need **Python 3.11**.
We advise creating a virtual environment first and install the dependencies there:

```bash
python3.11 -m venv venv
source venv/bin/activate
python -m pip install .
```

For development, you will need to install the optional dependencies as well:

```bash
source venv/bin/activate
python -m pip install ".[dev]"
```

Moreover, you are encouraged to install the pre-commit hooks, so that black, mypy and the unittests
run before every commit:
```bash
pre-commit install
```
You can run 
```bash
pre-commit run --all-files
```
To run pre-commit manually.

After installing the dependencies you can start the server. You have 3 options:

1. Run from your machine: 
```bash
cd src
python main.py --reload
```
The `--reload` argument will automatically restart the app if changes are made to the source files.
2. Run using docker. For instance using `scripts/run_apiserver.sh`
3. Run using DevContainer (see next subsection)

### Authentication
Currently, the code is by default running using the local Keycloak. To make 
this work, you need to set an environment variable. You can do this by setting the 
`KEYCLOAK_CLIENT_SECRET` in `src/.env`.

```bash
# src/.env
KEYCLOAK_CLIENT_SECRET=[SECRET]
```

Alternatively, you can connect to a different keycloak instance by modifying `src/.env`. EGI 
Checkin can for instance be used on a deployed instance - not on local host. Marco Rorro is the 
go-to person to request the usage of the EGI Checkin.

The reason that EGI Checkin doesn't work on localhost, is that the redirection url of EGI 
Checkin is strict - as it should be. On our development keycloak, any redirection url is 
accepted, so that it works on local host or wherever you deploy. This should never be the case 
for a production instance.

See [authentication README](developer/auth.md) for more information.

### Creating the Database

By default, the app will create a database on the provided MySQL server.
You can change this behavior through the **build-db** command-line parameter, 
it takes the following options:
  * never: *never* creates the database, not even if there does not exist one yet.
    Use this only if you expect the database to be created through other means, such
    as MySQL group replication.
  * if-absent: Creates a database only if none exists. (default)
  * drop-then-build: Drops the database on startup to recreate it from scratch.
    **THIS REMOVES ALL DATA PERMANENTLY. NO RECOVERY POSSIBLE.**

### Populating the Database
To populate the database with some examples, run the `connectors/fill-examples.sh` script.
When using `docker compose` you can easily do this by running the "examples" profile:
`docker compose --profile examples up`

## Usage

Following the installation instructions above, the server may be reached at `127.0.0.1:8000`.
REST API documentation is automatically built and can be viewed at `127.0.0.1:8000/docs`.


#### Automatically Restart on Change

If you want to automatically restart the server when a change is made to a file in the project, use the `--reload`
parameter.
It is important to realize that this also re-initializes the connection to the database, and possibly will do any
start-up work (e.g., populating the database).

#### Database Structure

The Python classes that define the database tables are found in [src/database/model/](../src/database/model/). 
The structure is based on the 
[metadata schema](https://github.com/aiondemand/metadata-schema).


## Adding resources

See [src/README.md](developer/code.md).

## Backups and Restoration

We provide several scripts to facilitate the scheduling of backups and the manual restoration of files. For details on these scripts and others, please see [scripts/README.md](scripts/README.md).

## Releases
