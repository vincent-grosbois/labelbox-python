from typing import Dict, List

from labelbox.orm.db_object import DbObject
from labelbox.orm.model import Field, Relationship


class Batch(DbObject):
    """ A Batch is a group of data rows submitted to a project for labeling

    Attributes:
        name (str)
        created_at (datetime)
        updated_at (datetime)
        deleted (bool)

        project (Relationship): `ToOne` relationship to Project
        created_by (Relationship): `ToOne` relationship to User

    """
    name = Field.String("name")
    created_at = Field.DateTime("created_at")
    updated_at = Field.DateTime("updated_at")
    deleted = Field.Boolean()
    size = Field.Int("size")

    # Relationships
    project = Relationship.ToOne("Project")
    created_by = Relationship.ToOne("User")

    def export_data_rows(self) -> List[Dict]:
        """Get the data rows associated with a batch"""

        gql = """query 
        
        """

        self.client.execute()

        return
