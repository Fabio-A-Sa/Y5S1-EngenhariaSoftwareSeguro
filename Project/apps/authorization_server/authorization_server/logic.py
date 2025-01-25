from sqlalchemy import select, and_

from authorization_server import db, logger
from authorization_server.models import Role, Operation


def can_role_perform_operation(role_name: str, resource: str) -> bool:
    role = db.session.execute(
        select(Role)
        .join(Role.operations)
        .where(and_(Role.name == role_name, Operation.resource == resource))
    ).scalar()
    
    logger.debug(f"Role: {role}")
    

    return role is not None
