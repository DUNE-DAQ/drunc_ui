from django.utils.safestring import SafeString

from controller.tables import toggle_button, toggle_text


def test_toggle_text_not_current():
    """Test the toggle_text function."""
    result = toggle_text("test", False)
    assert result == "TEST"


def test_toggle_text_current():
    """Test the toggle_text function."""
    result = toggle_text("test", True)
    assert isinstance(result, SafeString)
    assert result == '<span class="fw-bold text-primary">TEST</span>'


def test_toggle_button_not_current(mocker):
    """Test the toggle_button function when not current."""
    mocker.patch("controller.tables.reverse", return_value="/mocked_url/")
    result = toggle_button("event", False)
    assert isinstance(result, SafeString)
    assert (
        result == "<button disabled class='btn btn-secondary w-100 mx-2'>event</button>"
    )


def test_toggle_button_current(mocker):
    """Test the toggle_button function when current."""
    mocker.patch("controller.tables.reverse", return_value="/mocked_url/")
    result = toggle_button("event", True)
    assert isinstance(result, SafeString)
    assert (
        result
        == (
            "<button hx-post=/mocked_url/ hx-target='#state-machine' hx-include='#event_event' "  # noqa: E501
            "class='btn btn-success w-100 mx-2' >event</button>"
        )
    )
