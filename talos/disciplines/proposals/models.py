from pydantic import BaseModel


class AddDatasetParams(BaseModel):
    pass


class QueryResponse(BaseModel):
    answers: list[dict]


class RunParams(BaseModel):
    pass
