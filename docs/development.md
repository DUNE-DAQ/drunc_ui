# Development

<!-- markdownlint-disable next-line code-block-style -->
!!! note

    Make sure you've been through the instructions to run the project locally, can
    successfully run the web application under the Docker setup, have carried out the
    setup steps and can access the UI's you want to work with in the browser.

Working with the full functionality of the web application requires a number of services
to be started and to work in concert. The Docker Compose stack provides the required
services and is suitable for development and manual testing but is not suitable for
running QA (pre-commit) tooling or unit tests. The project directory is mounted into the
`app` service which allows the Django development server's auto-reload mechanism to
detect changes to local files and work as expected.

In addition to the Docker setup, you will also need to follow the below instructions on
working with poetry to run the project's QA tooling and unit tests.

## Working with Poetry

This is a Python application that uses [poetry](https://python-poetry.org) for packaging
and dependency management. It also provides [pre-commit](https://pre-commit.com/) hooks
for various linters and formatters and automated tests using
[pytest](https://pytest.org/) and [GitHub Actions](https://github.com/features/actions).
Pre-commit hooks are automatically kept updated with a dedicated GitHub Action.

To get started:

1. [Download and install Poetry](https://python-poetry.org/docs/#installation) following
   the instructions for your OS.

1. Clone this repository and make it your working directory

1. Set up the virtual environment:

    ```bash
    poetry install
    ```

1. Activate the virtual environment (alternatively, ensure any Python-related command is
   preceded by `poetry run`):

    ```bash
    poetry shell
    ```

1. Install the git hooks:

    ```bash
    pre-commit install
    ```

Pre-commit should now work as expected when making commits even without the need to have
an active poetry shell. You can also manually run pre-commit (e.g. `pre-commit run -a`)
and the unit tests with `pytest`. Remember you'll need to prefix these with `poetry run`
first if you don't have an active poetry shell.
