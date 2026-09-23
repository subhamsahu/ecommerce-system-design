from math import ceil

from sqlalchemy.orm import Query

from app.core.schemas import Page, Pagination


def paginate(query: Query, page: int, page_size: int, schema):
    total = query.order_by(None).count()
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    return Page(
        items=[schema.model_validate(row) for row in rows],
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=ceil(total / page_size) if total else 0,
        ),
    )