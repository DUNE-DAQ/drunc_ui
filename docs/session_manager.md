# Session Manager UI

<!-- markdownlint-disable next-line code-block-style -->
!!! note

    The session manager is currently in heavy development and do not represent the final
    design of it.

This provides:

- An index page containing:
    - a table displaying the currently running sessions.
    - a table displaying the available configurations.

The view functions for this UI are split into two categories:

- `pages` that load a full page.
- `partials` that load items within a page.

## Index Page

The page is composed primarily of two tables, one containing the active sessions with
the user in charge of them, and another containing the configurations available -
session id and the file that contains it.

Both tables are kept in sync with the backend by pulling up to date information at a set
interval. Available configurations are not likely to change regularly, but active
sessions and user information will. Like in other views, this is done via polling with
HTMX.

There is no search, filter or sorting implemented in the tables at the moment, but that
support could be added in the future, if needed.
