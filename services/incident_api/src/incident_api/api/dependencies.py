from flask import current_app

from incident_api.container import Container


def get_container() -> Container:
    container = current_app.config["CONTAINER"]

    if not isinstance(container, Container):
        raise RuntimeError("Application container is not configured")

    return container
