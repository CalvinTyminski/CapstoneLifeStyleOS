
from decimal import Decimal

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.store_item import StoreItem


items = [
    {
        "name": "City Park",
        "description": "Add a relaxing park to your virtual city.",
        "price": Decimal("150.00"),
        "category": "City Upgrade",
    },
    {
        "name": "Fitness Center",
        "description": "Add a fitness center to your virtual city.",
        "price": Decimal("300.00"),
        "category": "City Upgrade",
    },
    {
        "name": "Garden",
        "description": "Decorate your city with a garden.",
        "price": Decimal("75.00"),
        "category": "Decoration",
    },
    {
        "name": "Achievement Statue",
        "description": "Celebrate your lifestyle achievements.",
        "price": Decimal("200.00"),
        "category": "Decoration",
    },
]


def seed_store():
    with SessionLocal() as db:
        for item_data in items:
            existing = db.execute(
                select(StoreItem).where(
                    StoreItem.name == item_data["name"]
                )
            ).scalar_one_or_none()

            if existing is None:
                db.add(StoreItem(**item_data))

        db.commit()

    print("Store items seeded successfully!")


if __name__ == "__main__":
    seed_store()
