# Court and Tribunal Finder search

## Dependencies

- [docker-compose](https://docs.docker.com/compose/) for local development and testing

## Usage

#### `make dev`
Run a development environment with [ipdb](https://github.com/gotcha/ipdb)

If you need to run the app on a port other than `8000` you can set the exposed
port with the `PORT` environment variable.

`PORT=8002 make dev`

#### `make dev-psql`
Open a psql client in the dev Postgres container

#### `make dev-exec`
Get a docker exec prefix to run arbitrary commands against the dev app container.

For example:

#### `$(make dev-exec) python manage.py createsuperuser`
Create a Django superuser.

#### `$(make dev-exec) bash`
Open a bash shell

#### `make stop`
Stop all dev and test containers

#### `make rm`
Remove all dev and test containers

## Testing

#### `make test-unit`

Run unit tests

#### `make test-cucumber`
Run cucumber tests

#### `make test-psql`
Open a psql client in the test database

## Environment variables

The application uses the following environment variables.

* `FEEDBACK_EMAIL_SENDER`: the from address of the feedback emails sent by the application
* `FEEDBACK_EMAIL_RECEIVER`: the email addresses of the recipients of the feedback emails (comma separated)
* `SMTP_HOSTNAME`
* `SMTP_PASSWORD`
* `SMTP_PORT`
* `SMTP_USERNAME`: SMTP details for sending feedback emails
* `SENTRY_URL`: for monitoring. See <https://getsentry.com/>
* `S3_KEY`, `S3_BUCKET`, `S3_SECRET`: the `populate-db` command above either reads the court data from local files or, if those variables are set, from an S3 bucket.
