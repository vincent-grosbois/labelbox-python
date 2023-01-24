import pytest
import os
from labelbox_dev import Session


@pytest.fixture(scope="session", autouse=True)
def session():
    api_key = os.environ.get('LABELBOX_TEST_API_KEY_LOCAL')
    Session.initialize(base_api_url="http://host.docker.internal:8080",
                       api_key=api_key)
