from pydantic import BaseModel, Field


class CreateIncidentRequest(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    severity: str
    service_name: str = Field(min_length=1, max_length=100)
    owner_team: str | None = Field(default=None, max_length=100)


class IncidentResponse(BaseModel):
    id: str
    title: str
    description: str | None
    severity: str
    status: str
    service_name: str
    owner_team: str | None


class ListIncidentsResponse(BaseModel):
    items: list[IncidentResponse]
    limit: int
    offset: int
    count: int


class ChangeIncidentSeverityRequest(BaseModel):
    severity: str


class ChangeIncidentStatusRequest(BaseModel):
    status: str
