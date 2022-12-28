import logging

import flask_migrate
from . import app, db, PlaceReview


def upgrade():
    with app.app_context():
        flask_migrate.upgrade()


def delete_place_review(ids):
    with app.app_context():
        if len(ids) == 0:
            logging.warning(
                "At least on id must be specified. Usage: flask delete_place_review 1 2 3."
            )

        place_reviews = (
            db.session.query(PlaceReview).filter(PlaceReview.id.in_(ids)).all()
        )
        removed_ids = []
        for place_review in place_reviews:
            db.session.delete(place_review)
            removed_ids.append(place_review.id)

        db.session.commit()

        if len(place_reviews) < len(ids):
            logging.warning(
                f"Some ids were not found in the database: {set(ids).difference(set(removed_ids))}."
            )
