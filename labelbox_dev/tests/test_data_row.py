from labelbox_dev.data_row import DataRow
from labelbox_dev.dataset import Dataset
from labelbox_dev.session import Session

import pytest
import uuid

from unittest.mock import patch


@pytest.fixture(scope="session")
def dataset():
    dataset = Dataset.create({"name": "Test", "description": "Test dataset"})

    yield dataset

    dataset.delete()


@pytest.fixture(scope="session")
def datarows(dataset):
    data_rows = [{
        "row_data":
            f"https://storage.googleapis.com/labelbox-datasets/image_sample_data/image-sample-{i}.jpg",
        "global_key":
            f"https://storage.googleapis.com/labelbox-datasets/image_sample_data/image-sample-{i}.jpg"
            + str(uuid.uuid4()),
    } for i in range(5)]
    datarows = DataRow.create(dataset.id, data_rows)

    yield datarows

    for dr in datarows:
        dr.delete()


def test_get_data_rows_by_global_keys(datarows):
    global_keys = [dr.global_key for dr in datarows]
    data_rows_iterator = DataRow.get_by_global_keys(global_keys)

    # Test pagination
    data_rows_iterator.limit = 2
    with patch.object(Session, 'get_request',
                      wraps=Session.get_request) as mock:
        drs = list(data_rows_iterator)
        assert mock.call_count == 3
    assert len(drs) == 5

    retrived_global_keys = {dr.global_key for dr in drs}
    assert retrived_global_keys == set(global_keys)


def test_get_data_rows_by_ids(datarows):
    ids = [dr.id for dr in datarows]
    data_rows_iterator = DataRow.get_by_ids(ids)

    # Test pagination
    data_rows_iterator.limit = 2
    with patch.object(Session, 'get_request',
                      wraps=Session.get_request) as mock:
        drs = list(data_rows_iterator)
        assert mock.call_count == 3
    assert len(drs) == 5

    retrived_ids = {dr.id for dr in drs}
    assert retrived_ids == set(ids)
