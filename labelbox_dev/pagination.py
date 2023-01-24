from abc import abstractmethod
from collections import deque

from labelbox_dev.session import Session

DEFAULT_LIMIT = 100
DATA_KEY = 'data'
CURSOR_KEY = 'next'
LIMIT_KEY = 'limit'
IDS_KEY = 'ids'


class BasePaginator:

    def __init__(self, resource, entity_class, params, limit):
        self.resource = resource
        self.entity_class = entity_class
        self.limit = limit
        self.params = params if params else {}
        self._is_last_page = False
        self._entities_from_last_page = deque()
        self._session = Session

    def __iter__(self):
        return self

    @abstractmethod
    def get_next_page():
        ...

    def deserialize_entity(self, entity):
        """Creates an entity object from JSON object. This can be overridden in a subclass to change instantiation behaviour."""
        return self.entity_class(entity)

    def __next__(self):
        if self._entities_from_last_page:
            return self._entities_from_last_page.pop()
        elif self._is_last_page:  # Order of these conditions is important
            raise StopIteration
        else:
            page = self.get_next_page()
            entities = [self.deserialize_entity(entity) for entity in page]
            self._entities_from_last_page = entities
            return next(self)


class IdentifierPaginator(BasePaginator):

    def __init__(self,
                 resource,
                 entity_class,
                 identifiers,
                 params=None,
                 limit=DEFAULT_LIMIT,
                 identifiers_key=IDS_KEY):
        self.resource = resource
        self.entity_class = entity_class
        self.identifiers = identifiers
        self.identifiers_key = identifiers_key
        self.limit = limit
        self._current_idx = 0
        super().__init__(resource, entity_class, params, limit)

    def get_next_page(self):
        end_idx = self._current_idx + self.limit
        ids = self.identifiers[self._current_idx:end_idx]
        self._current_idx += self.limit
        if self._current_idx >= len(self.identifiers):
            self._is_last_page = True

        ids_str = ','.join(ids)
        params = self.params.copy()
        params.update({self.identifiers_key: ids_str})
        response = self._session.get_request(self.resource, params)
        return response
