from pydantic import BaseModel


class Command(BaseModel):
  count: int