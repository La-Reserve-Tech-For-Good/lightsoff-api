import datetime
import logging
import os

import click
import sqlalchemy as sa
import requests

from enum import Enum
from flask import current_app
from flask_cors import CORS
from flask_migrate import Migrate
from flask_openapi3 import OpenAPI
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus
from pydantic import BaseModel, Field, root_validator
from typing import Optional

app = OpenAPI(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")

CORS(app, origins=os.environ.get("CORS_ALLOWED_ORIGINS", "").split(","))
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Place(db.Model):
    google_place_id = sa.Column(sa.Text, primary_key=True, autoincrement=False)
    name = sa.Column(sa.Text, nullable=False)
    created_at = sa.Column(
        sa.DateTime, nullable=False, default=lambda: datetime.datetime.utcnow()
    )
    address = sa.Column(sa.Text, nullable=False)
    google_place_url = sa.Column(sa.Text)
    phone_number = sa.Column(sa.String(length=15))
    report_count = sa.Column(sa.Integer, nullable=False, default=1)
    latitude = sa.Column(sa.Float, nullable=False)
    longitude = sa.Column(sa.Float, nullable=False)


class PlaceReview(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    google_place_id = sa.Column(
        sa.Text,
        sa.ForeignKey("place.google_place_id", name="place_review_place_fkey"),
        nullable=False,
    )
    created_at = sa.Column(sa.DateTime, nullable=False)
    completed_at = sa.Column(sa.DateTime)
    type = sa.Column(sa.String(50))
    do_it_for_me = sa.Column(sa.Boolean, default=False)


class PlacePath(BaseModel):
    google_place_id: str


class PlaceBody(BaseModel):
    google_place_id: str
    name: str
    google_place_url: str
    address: str
    phone_number: Optional[str]
    latitude: float
    longitude: float

    class Config:
        orm_mode = True


class PlaceResponse(BaseModel):
    code: int = Field(0, description="Status Code")
    message: str = Field("ok", description="Exception Information")


@app.post("/places", responses={"200": PlaceResponse})
def create_place(body: PlaceBody):
    place = (
        db.session.query(Place)
        .filter(Place.google_place_id == body.google_place_id)
        .first()
    )

    if not place:
        db.session.add(Place(**body.dict()))
    else:
        place.report_count += 1

    db.session.commit()

    return {
        "code": HTTPStatus.OK.value,
        "message": HTTPStatus.OK.description,
    }, HTTPStatus.OK


class PlaceReviewType(str, Enum):
    GOOGLE_REVIEW = "GOOGLE_REVIEW"
    PHONE_CALL = "PHONE_CALL"
    TWILIO = "TWILIO"


class PlaceReviewBody(BaseModel):
    type: Optional[PlaceReviewType]
    do_it_for_me: Optional[bool]

    class Config:
        orm_mode = True

    @root_validator
    def consistency_check(cls, values):
        if values["do_it_for_me"] is None and not values["type"]:
            raise ValueError("type or do_it_for_me fields should not be null")

        if values["do_it_for_me"] and values["type"]:
            raise ValueError("type or do_it_for_me fields should be null")

        if not values["do_it_for_me"] and "type" in values and not values["type"]:
            raise ValueError("type field should not be null")

        if values.get("type"):
            values["type"] = values["type"].value

        return values


class PlaceReviewResponse(BaseModel):
    code: int = Field(0, description="Status Code")
    message: str = Field("ok", description="Exception Information")


@app.post(
    "/places/<string:google_place_id>/reviews", responses={"200": PlaceReviewResponse}
)
def create_place_review(path: PlacePath, body: PlaceReviewBody):
    place = (
        db.session.query(Place)
        .filter(Place.google_place_id == path.google_place_id)
        .first()
    )

    if not place:
        return {
            "code": HTTPStatus.NOT_FOUND.value,
            "message": HTTPStatus.NOT_FOUND.description,
        }, HTTPStatus.NOT_FOUND

    place_review = PlaceReview(
        google_place_id=place.google_place_id,
        created_at=datetime.datetime.utcnow(),
        completed_at=datetime.datetime.utcnow() if not body.do_it_for_me else None,
        **body.dict(),
    )
    db.session.add(place_review)

    payload = {
        "place_name": place.name,
        "google_place_url": place.google_place_url,
        "place_address": place.address,
        "review_type": place_review.type,
    }

    db.session.commit()

    if hook_url := os.environ.get("CREATE_REVIEW_ZAPPIER_HOOK_URL"):
        try:
            requests.post(hook_url, json=payload)
        except Exception as e:
            current_app.logger.error(e)

    return {
        "code": HTTPStatus.OK.value,
        "message": HTTPStatus.OK.description,
    }, HTTPStatus.OK


@app.cli.command("delete_place_review")
@click.argument("ids", nargs=-1)
def delete_place_review(ids):
    if len(ids) == 0:
        logging.warning("At least on id must be specified. Usage: flask delete_place_review 1 2 3.")

    place_reviews = (
        db.session.query(PlaceReview)
        .filter(PlaceReview.id.in_(ids))
        .all()
    )
    removed_ids = []
    for place_review in place_reviews:
        db.session.delete(place_review)
        removed_ids.append(str(place_review.id))

    db.session.commit()

    if len(place_reviews) < len(ids):
        logging.warning(f"Some ids were not found in the database: {set(ids).difference(set(removed_ids))}.")


if __name__ == "__main__":
    app.run()
