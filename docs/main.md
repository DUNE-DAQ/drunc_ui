# Main application

This application provides functionality shared between other applications, to avoid
unnecessary duplication.

The main things the `main` app provides are:

- Base HTML templates including the navigation bar and basic dependencies.
- User registration page and login.
- Message feed-related models, tables, views and templates.
- Django commands, extending the functionality of `manage.py`.

In terms of specific UIs, this app provides:

- An index page containing:
    - the drunc UI landing page, currently containing just buttons to navigate to other applications (eg. process manager)
- A help page, currently empty

The view functions for this UI are split into two categories:

- `pages` that load a full page.
- `partials` that load items within a page.

## HTML templates

The HTML templates ensure the visual consistency of the application. The main ones are:

### Navigation bar

This contains the DUNE logo, link to the help page, login and registration pages, and
links to the individual applications. These are visible only when the user is logged in.

### Base template

Base HTML document for all the pages within the Drunc UI. Any other template for full
pages (not for partials) should include this one with a `{% extends "main/base.html" %}`
directive at the top.

It loads some dependencies like HTMX, hyperscript or bootstrap, includes the navigation
bar and defines some of the basic layout of the page.

## Index page

Landing page for the Drunc UI application. Currently only contains buttons for the
individual apps, already contained in the navigation bar, anyway.

## Message feed

The message feed is used in other applications, filtered there to report only on
messages of a certain topic or to be displayed in certain areas of the page. The
underlying functionality is the same in all cases, and hence it is included in the main
app.

The way the message system works is as follow:

- Messages received with the topics indicated in the application settings are ingested
by the [Kafka consumer](#kafka-consumer) and stored in the database.
- Messages in the database older than a certain expiry time are deleted from the
database.
- Messages of the chosen topic are pulled from the database by each application and
displayed using the tables and partial views provided by this app.

## Commands

The functionality of the standard `manage.py` Django script that serves as entry point
for all of its functionality has been expanded with the following extra commands:

### Kafka consumer

Call with:

```bash
python manage.py kafka_consumer
```

The Kafka consumer is in charge of listening for new messages broadcast by the Kafka
server on certain topics, process them and then save them in the database for later use
by the other apps within Drunc UI.

The main configuration options, defined in the settings, are:

- `KAFKA_ADDRESS`: Where the Kafka server is running.
- `KAFKA_TOPIC_REGEX`: Dictionary with the name and topics (as a regex string) to be
  listen to.
- `MESSAGE_EXPIRE_SECS`: Time after which messages in the database will be deleted.

### Store message

Call with:

```bash
python manage.py store_message
```

Simple command line tool to manually add messages to the database. Mainly used for
testing purposes.
