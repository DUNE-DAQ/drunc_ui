# TLDR Testing

Create a DUNE-DAQ environment as usual.

Install `drunc_ui` with `pip install /path/to/drunc_ui`.

Run `drunc-ui-manage migrate` to create and migrate a database (db.sqlite3 in current directory).

Create a test user with `drunc-ui-manage createsuperuser`, following prompts.

Start an instance of `drunc-unified-shell`, noting its host and port, and boot the session:

```bash
drunc-unified-shell ssh-standalone config/daqsystemtest/example-configs.data.xml local-1x1-config JamesTest

# Inside the shell:
drunc-unified-shell > boot
```

Start an instance of `drunc-session-manager`, noting its host and port.

```bash
drunc-session-manager
```

Set up environment variables:

```bash
export PROCESS_MANAGER_URL=...  # process manager host:port
export SESSION_MANAGER_URL=...  # session manager host:port
export CSC_URL=...  # connectivity service host:port
export CSC_SESSION=...  # connectivity service session, e.g. JamesTest
```

Now start the drunc_ui server with `drunc-ui-manage runserver` or `drunc-ui-run-gunicorn`.

Point your browser to the server and login. For `runserver`, it's `http://127.0.0.1:8000/`.
