"""Request and response bodies of the JSON API."""

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    name: str = Field(examples=["Jane Doe"])
    email: str = Field(examples=["jane.doe@example.com"])
    password: str = Field(examples=["secret123"], description="At least 6 characters")


class LoginRequest(BaseModel):
    email: str = Field(examples=["jane.doe@example.com"])
    password: str = Field(examples=["secret123"])


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


class RegisterResponse(UserResponse):
    access_token: str


class LoginResponse(BaseModel):
    id: int
    access_token: str


class OkResponse(BaseModel):
    ok: bool = True


# --- Autopilots, stations, orders ---


class AutopilotIdResponse(BaseModel):
    id: int


class StationOut(BaseModel):
    number: int
    name: str
    color: str = Field(description="Line color, a CSS color name")


class StationsResponse(BaseModel):
    stations: list[StationOut]


class TrackResponse(BaseModel):
    track: int = Field(description="Random unique 5-digit order number")


class OrderOut(BaseModel):
    id: int
    track: int
    firstName: str
    lastName: str
    address: str
    station: StationOut
    phone: str
    rentTime: int
    deliveryDate: str = Field(description="YYYY-MM-DD")
    comment: str
    color: list[str]
    status: str = Field(description="hangar | heading | on_site | flying | ended | delayed")
    autopilotId: int | None
    autopilotFirstName: str | None
    createdAt: str
    acceptedAt: str | None
    finishedAt: str | None
    rentalEndsAt: str | None


class OrderResponse(BaseModel):
    order: OrderOut


class OrdersResponse(BaseModel):
    orders: list[OrderOut]


# --- Shipyard ---


class ShipyardPartOut(BaseModel):
    id: int
    category: str = Field(description="hull | engine | module")
    name: str
    price: int = Field(description="Credits")
    description: str
    mass: int = Field(description="t")
    power: int = Field(description="MW")
    cargo: int = Field(description="m3")
    comfort: int = Field(description="Stars, 1-5")


class ShipyardPartsResponse(BaseModel):
    parts: list[ShipyardPartOut]


class ShipyardOrderCreated(BaseModel):
    number: int
    total: int = Field(description="Computed by the server; the hull counts twice")


class ShipyardOrderItemOut(BaseModel):
    id: int
    category: str
    name: str
    price: int


class ShipyardOrderOut(BaseModel):
    number: int
    total: int
    createdAt: str
    parts: list[ShipyardOrderItemOut]


class ShipyardOrdersResponse(BaseModel):
    orders: list[ShipyardOrderOut]
