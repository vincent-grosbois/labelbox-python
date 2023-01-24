from labelbox_dev.pagination import IdentifierPaginator
from labelbox_dev.entity import Entity
from unittest.mock import MagicMock


def test_identifier_paginator():
    ids = [str(id_) for id_ in range(0, 1000, 200)]
    paginator = IdentifierPaginator('resource',
                                    Entity,
                                    ids, {'param1': 'val1'},
                                    limit=2)
    paginator._session = MagicMock()
    return_value = [{'id': ids[0]}, {'id': ids[1]}]
    paginator._session.get_request = MagicMock(return_value=return_value)
    items = list(paginator)
    assert len(items) == 6
    assert isinstance(items[0], Entity)
    assert paginator._session.get_request.call_count == 3
