# Court and Tribunal Finder search

## Dependencies

- [docker-compose](https://docs.docker.com/compose/) for local development and testing

## Usage

To run a development environment with [ipdb](https://github.com/gotcha/ipdb)

`make dev`

If you need to run the app on a port other than `8000` you can set the exposed
port with the `PORT` environment variable.

`PORT=8002 make dev`

To open a psql client in the dev Postgres container

`make dev-psql`

To stop all dev and test containers

`make stop`

To remove all dev and test containers

`make rm`

## Testing

To run unit tests

`make test-unit`

To run cucumber tests

`make test-cucumber`

To open a psql client in the test Postgres container

`make test-psql`

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
