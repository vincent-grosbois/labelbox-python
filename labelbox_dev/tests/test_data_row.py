from labelbox_dev.data_row import DataRow
from labelbox_dev.dataset import Dataset
from labelbox_dev.session import Session
import uuid

from unittest.mock import patch


def test_data_row_get_by_global_keys_pagination():

    Session.initialize("http://host.docker.internal:8080", api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJjbGIydzgwMzQwMDBiamJ4cDRnbTZhbDZlIiwib3JnYW5pemF0aW9uSWQiOiJjbGIydzgwMGIwMDBhamJ4cDNvYzc3eDV0IiwiYXBpS2V5SWQiOiJjbGJlNXQzcm0wMDBha3ZjOThhcmowdDJvIiwic2VjcmV0IjoiZjFlZDIzYmI0ODUwNzlmNjNiNjBiYzBiM2ZhMGNlYTgiLCJpYXQiOjE2NzA0NDgzMzQsImV4cCI6MjMwMTYwMDMzNH0.EOmkqEVMr38JGuxhaCyoR6y0cY6wPsVLgWAYGmSQIxg")

    dataset = Dataset.create({
        "name": "Test",
        "description": "Test dataset"
    })

    data_rows = [
        {
            "row_data": f"https://storage.googleapis.com/labelbox-datasets/image_sample_data/image-sample-{i}.jpg",
            "global_key": f"https://storage.googleapis.com/labelbox-datasets/image_sample_data/image-sample-{i}.jpg" + str(uuid.uuid4()),
        } for i in range(5)
    ]
    datarows = DataRow.create(dataset.id, data_rows)
    global_keys = [dr.global_key for dr in datarows]

    retrieved_data_rows = DataRow.get_by_global_keys(global_keys, page_size=2)
    with patch.object(Session, 'post_request', wraps=Session.post_request) as mock:
        drs = list(retrieved_data_rows)
        assert mock.call_count == 3
    assert len(drs) == 5

    for dr in drs:
        assert isinstance(dr, DataRow)
        assert dr.row_data.startswith('https://storage.googleapis.com/labelbox-datasets/image_sample_data/image-sample-')