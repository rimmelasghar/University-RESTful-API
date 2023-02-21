from connection import session
from models import loginTable
from schema import User
res = session.query(loginTable).filter(loginTable.username == "string").first()
res.full_name = "Rimmel asghar"
session.commit()
print(res)
