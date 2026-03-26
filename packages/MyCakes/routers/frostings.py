from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from models import FrostingIn, FrostingOut, FrostingSummary

router = APIRouter()


async def _fetch_frosting(db, frosting_id: int) -> dict:
    row = await db.execute("SELECT * FROM frostings WHERE id = ?", (frosting_id,))
    f = await row.fetchone()
    if not f:
        raise HTTPException(404, "Tynk nie istnieje")
    return dict(f)


async def _fetch_ingredients(db, frosting_id: int) -> list:
    cur = await db.execute(
        "SELECT * FROM frosting_ingredients WHERE frosting_id = ? ORDER BY id", (frosting_id,)
    )
    return [dict(r) for r in await cur.fetchall()]


async def _fetch_steps(db, frosting_id: int) -> list:
    cur = await db.execute(
        "SELECT * FROM frosting_steps WHERE frosting_id = ? ORDER BY position, id", (frosting_id,)
    )
    return [dict(r) for r in await cur.fetchall()]


async def _rating(db, frosting_id: int) -> tuple:
    cur = await db.execute(
        "SELECT AVG(rating), COUNT(*) FROM reviews WHERE target_type='frosting' AND target_id=?",
        (frosting_id,)
    )
    row = await cur.fetchone()
    avg = round(row[0], 1) if row[0] else None
    return avg, row[1]


async def _build_out(db, f: dict) -> FrostingOut:
    avg, cnt = await _rating(db, f["id"])
    return FrostingOut(
        **f,
        ingredients=await _fetch_ingredients(db, f["id"]),
        steps=await _fetch_steps(db, f["id"]),
        avg_rating=avg,
        review_count=cnt,
    )


async def _insert_ingredients(db, frosting_id: int, ingredients: list):
    for ing in ingredients:
        name = ing.name if hasattr(ing, 'name') else ing['name']
        amount = ing.amount if hasattr(ing, 'amount') else ing['amount']
        unit = ing.unit if hasattr(ing, 'unit') else ing['unit']
        await db.execute(
            "INSERT INTO frosting_ingredients (frosting_id, name, amount, unit) VALUES (?,?,?,?)",
            (frosting_id, name, amount, unit)
        )


async def _insert_steps(db, frosting_id: int, steps: list):
    for step in steps:
        if hasattr(step, 'position'):
            pos, title, desc, time_min, stage = step.position, step.title, step.description, step.time_min, step.stage
        else:
            pos, title, desc, time_min, stage = step['position'], step['title'], step['description'], step['time_min'], step.get('stage', 'Dzień 1')
        await db.execute(
            "INSERT INTO frosting_steps (frosting_id, position, title, description, time_min, stage) VALUES (?,?,?,?,?,?)",
            (frosting_id, pos, title, desc, time_min, stage)
        )


@router.get("", response_model=list[FrostingSummary])
async def list_frostings(db=Depends(get_db)):
    cur = await db.execute("SELECT * FROM frostings ORDER BY name")
    rows = [dict(r) for r in await cur.fetchall()]
    result = []
    for f in rows:
        avg, cnt = await _rating(db, f["id"])
        result.append(FrostingSummary(**f, avg_rating=avg, review_count=cnt))
    return result


@router.get("/{frosting_id}", response_model=FrostingOut)
async def get_frosting(frosting_id: int, db=Depends(get_db)):
    f = await _fetch_frosting(db, frosting_id)
    return await _build_out(db, f)


@router.post("", response_model=FrostingOut, status_code=201)
async def create_frosting(data: FrostingIn, db=Depends(get_db)):
    cur = await db.execute(
        """INSERT INTO frostings (name, description, type, ref_diameter_cm, ref_height_cm, prep_time_min)
           VALUES (?,?,?,?,?,?)""",
        (data.name, data.description, data.type, data.ref_diameter_cm, data.ref_height_cm, data.prep_time_min)
    )
    fid = cur.lastrowid
    await _insert_ingredients(db, fid, data.ingredients)
    await _insert_steps(db, fid, data.steps)
    await db.commit()
    return await _build_out(db, await _fetch_frosting(db, fid))


@router.put("/{frosting_id}", response_model=FrostingOut)
async def update_frosting(frosting_id: int, data: FrostingIn, db=Depends(get_db)):
    await _fetch_frosting(db, frosting_id)
    await db.execute(
        """UPDATE frostings SET name=?, description=?, type=?, ref_diameter_cm=?, ref_height_cm=?,
           prep_time_min=?, updated_at=datetime('now') WHERE id=?""",
        (data.name, data.description, data.type, data.ref_diameter_cm, data.ref_height_cm,
         data.prep_time_min, frosting_id)
    )
    await db.execute("DELETE FROM frosting_ingredients WHERE frosting_id=?", (frosting_id,))
    await db.execute("DELETE FROM frosting_steps WHERE frosting_id=?", (frosting_id,))
    await _insert_ingredients(db, frosting_id, data.ingredients)
    await _insert_steps(db, frosting_id, data.steps)
    await db.commit()
    return await _build_out(db, await _fetch_frosting(db, frosting_id))


@router.post("/{frosting_id}/clone", response_model=FrostingOut, status_code=201)
async def clone_frosting(frosting_id: int, db=Depends(get_db)):
    original = await _fetch_frosting(db, frosting_id)
    ingredients = await _fetch_ingredients(db, frosting_id)
    steps = await _fetch_steps(db, frosting_id)

    cur = await db.execute(
        """INSERT INTO frostings (name, description, type, ref_diameter_cm, ref_height_cm, prep_time_min)
           VALUES (?,?,?,?,?,?)""",
        (original["name"] + " (kopia)", original["description"], original["type"],
         original.get("ref_diameter_cm", 24.0), original.get("ref_height_cm", 10.0),
         original["prep_time_min"])
    )
    new_id = cur.lastrowid
    await _insert_ingredients(db, new_id, ingredients)
    await _insert_steps(db, new_id, steps)
    await db.commit()
    return await _build_out(db, await _fetch_frosting(db, new_id))


@router.delete("/{frosting_id}", status_code=204)
async def delete_frosting(frosting_id: int, db=Depends(get_db)):
    await _fetch_frosting(db, frosting_id)
    await db.execute("DELETE FROM frostings WHERE id=?", (frosting_id,))
    await db.commit()
