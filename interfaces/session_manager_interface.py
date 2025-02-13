"""Interface for the session manager endpoint."""


def get_configs() -> list[dict[str, str]]:
    """Get the available configurations for the controller.

    TODO: Placeholder function with hardcoded values. Pull data dynamically when the
    relevant endpoint is implemented.

    Returns:
        List of dictionaries indicating the file where the config is contained and the
        id for the config.
    """
    return [
        {
            "file": "example-configs.data.xml",
            "id": "ehn1-local-1x1-config",
        },
        {
            "file": "example-configs.data.xml",
            "id": "ehn1-local-2x3-config",
        },
        {
            "file": "example-configs.data.xml",
            "id": "local-1x1-config",
        },
        {
            "file": "example-configs.data.xml",
            "id": "local-2x3-config",
        },
    ]


def get_sessions() -> list[dict[str, str]]:
    """Get the active sessions in the controller.

    TODO: Placeholder function with hardcoded values. Pull data dynamically when the
    relevant endpoint is implemented.

    Returns:
        List of dictionaries indicating the session name and the actor name (i.e.
        typically, the user who boots the session).
    """
    actors = ["Alice", "Bob", "Gandalf"]
    names = [
        "a8098c1a-f86e-11da-bd1a-00112444be1e",
        "6fa459ea-ee8a-3ca4-894e-db77e160355e",
        "16fd2706-8baf-433b-82eb-8c7fada847da",
    ]
    return [
        {
            "name": name,
            "actor": actor,
        }
        for name, actor in zip(names, actors)
    ]
