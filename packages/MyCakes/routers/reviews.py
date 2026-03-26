from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from database import get_db
from models import ReviewIn, ReviewOut

router = APIRouter()

VALID_TYPES = {"cake", "layer", "frosting"}


@router.get("", response_model=list[ReviewOut])
async def list_reviews(
    target_type: Optional[str] = Query(None),
    target_id: Optional[int] = Query(None),
    db=Depends(get_db),
):
    if target_type and target_type not in VALID_TYPES:
        raise HTTPException(400, f"target_type musi być jednym z: {VALID_TYPES}")

    if target_type and target_id:
        cur = await db.execute(
            "SELECT * FROM reviews WHERE target_type=? AND target_id=? ORDER BY created_at DESC",
            (target_type, target_id)
        )
    elif target_type:
        cur = await db.execute(
            "SELECT * FROM reviews WHERE target_type=? ORDER BY created_at DESC",
            (target_type,)
        )
    else:
        cur = await db.execute("SELECT * FROM reviews ORDER BY created_at DESC")

    return [dict(r) for r in await cur.fetchall()]


@router.get("/{target_type}/{target_id}", response_model=list[ReviewOut])
async def get_reviews(target_type: str, target_id: int, db=Depends(get_db)):
    if target_type not in VALID_TYPES:
        raise HTTPException(400, f"target_type musi być jednym z: {VALID_TYPES}")
    cur = await db.execute(
        "SELECT * FROM reviews WHERE target_type=? AND target_id=? ORDER BY created_at DESC",
        (target_type, target_id)
    )
    return [dict(r) for r in await cur.fetchall()]


@router.post("", response_model=ReviewOut, status_code=201)
async def create_review(data: ReviewIn, db=Depends(get_db)):
    if data.target_type not in VALID_TYPES:
        raise HTTPException(400, f"target_type musi być jednym z: {VALID_TYPES}")
    if not (1 <= data.rating <= 5):
        raise HTTPException(400, "Ocena musi być między 1 a 5")
    cur = await db.execute(
        "INSERT INTO reviews (target_type, target_id, author, text, rating) VALUES (?,?,?,?,?)",
        (data.target_type, data.target_id, data.author, data.text, data.rating)
    )
    await db.commit()
    row = await db.execute("SELECT * FROM reviews WHERE id=?", (cur.lastrowid,))
    return dict(await row.fetchone())


@router.delete("/{review_id}", status_code=204)
async def delete_review(review_id: int, db=Depends(get_db)):
    cur = await db.execute("SELECT id FROM reviews WHERE id=?", (review_id,))
    if not await cur.fetchone():
        raise HTTPException(404, "Opinia nie istnieje")
    await db.execute("DELETE FROM reviews WHERE id=?", (review_id,))
    await db.commit()
