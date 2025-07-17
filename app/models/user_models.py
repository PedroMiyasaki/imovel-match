from pydantic import BaseModel
from pydantic import Field
import duckdb

class UserInput(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        
    user_name: str = Field(..., description="The name of the user")
    connection: duckdb.DuckDBPyConnection = Field(..., description="Connection with the database")