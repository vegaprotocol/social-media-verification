# This file is automatically picked up and run by pytest
# It defines special marker: `@pytest.mark.focus`


def pytest_collection_modifyitems(items):
    """If any items are marked 'focus', run only those items.

    This hook is run automatically by pytest.
    """
    # Find items with the 'focus' mark
    focused = [item for item in items if item.get_closest_marker("focus")]
    # If any have it, replace the full list of collected items with only them
    if focused:
        items[:] = focused


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "focus: If any tests have this mark, run only those"
    )
