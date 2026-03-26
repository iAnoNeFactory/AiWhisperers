from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from models import LayerIn, LayerOut, LayerSummary

router = APIRouter()


async def _fetch_layer(db, layer_id: int) -> dict:
    row = await db.execute("SELECT * FROM layers WHERE id = ?", (layer_id,))
    layer = await row.fetchone()
    if not layer:
        raise HTTPException(404, "Warstwa nie istnieje")
    return dict(layer)


async def _fetch_ingredients(db, layer_id: int) -> list:
    cur = await db.execute(
        "SELECT * FROM layer_ingredients WHERE layer_id = ? ORDER BY id", (layer_id,)
    )
    return [dict(r) for r in await cur.fetchall()]


async def _fetch_steps(db, layer_id: int) -> list:
    cur = await db.execute(
        "SELECT * FROM layer_steps WHERE layer_id = ? ORDER BY position, id", (layer_id,)
    )
    return [dict(r) for r in await cur.fetchall()]


async def _rating(db, layer_id: int) -> tuple:
    cur = await db.execute(
        "SELECT AVG(rating), COUNT(*) FROM reviews WHERE target_type='layer' AND target_id=?",
        (layer_id,)
    )
    row = await cur.fetchone()
    avg = round(row[0], 1) if row[0] else None
    return avg, row[1]


async def _build_layer_out(db, layer: dict) -> LayerOut:
    avg, cnt = await _rating(db, layer["id"])
    return LayerOut(
        **layer,
        ingredients=await _fetch_ingredients(db, layer["id"]),
        steps=await _fetch_steps(db, layer["id"]),
        avg_rating=avg,
        review_count=cnt,
    )


async def _insert_ingredients(db, layer_id: int, ingredients: list):
    for ing in ingredients:
        await db.execute(
            "INSERT INTO layer_ingredients (layer_id, name, amount, unit) VALUES (?,?,?,?)",
            (layer_id, ing.name if hasattr(ing, 'name') else ing['name'],
             ing.amount if hasattr(ing, 'amount') else ing['amount'],
             ing.unit if hasattr(ing, 'unit') else ing['unit'])
        )


async def _insert_steps(db, layer_id: int, steps: list):
    for step in steps:
        if hasattr(step, 'position'):
            pos, title, desc, time_min, stage = step.position, step.title, step.description, step.time_min, step.stage
        else:
            pos, title, desc, time_min, stage = step['position'], step['title'], step['description'], step['time_min'], step.get('stage', 'Dzień 1')
        await db.execute(
            "INSERT INTO layer_steps (layer_id, position, title, description, time_min, stage) VALUES (?,?,?,?,?,?)",
            (layer_id, pos, title, desc, time_min, stage)
        )


@router.get("", response_model=list[LayerSummary])
async def list_layers(db=Depends(get_db)):
    cur = await db.execute("SELECT * FROM layers ORDER BY name")
    layers = [dict(r) for r in await cur.fetchall()]
    result = []
    for l in layers:
        avg, cnt = await _rating(db, l["id"])
        result.append(LayerSummary(**l, avg_rating=avg, review_count=cnt))
    return result


@router.get("/{layer_id}", response_model=LayerOut)
async def get_layer(layer_id: int, db=Depends(get_db)):
    layer = await _fetch_layer(db, layer_id)
    return await _build_layer_out(db, layer)


@router.post("", response_model=LayerOut, status_code=201)
async def create_layer(data: LayerIn, db=Depends(get_db)):
    cur = await db.execute(
        """INSERT INTO layers (name, description, category, default_height_cm,
           default_diameter_cm, prep_time_min, bake_time_min)
           VALUES (?,?,?,?,?,?,?)""",
        (data.name, data.description, data.category, data.default_height_cm,
         data.default_diameter_cm, data.prep_time_min, data.bake_time_min)
    )
    layer_id = cur.lastrowid
    await _insert_ingredients(db, layer_id, data.ingredients)
    await _insert_steps(db, layer_id, data.steps)
    await db.commit()
    return await _build_layer_out(db, await _fetch_layer(db, layer_id))


@router.put("/{layer_id}", response_model=LayerOut)
async def update_layer(layer_id: int, data: LayerIn, db=Depends(get_db)):
    await _fetch_layer(db, layer_id)
    await db.execute(
        """UPDATE layers SET name=?, description=?, category=?, default_height_cm=?,
           default_diameter_cm=?, prep_time_min=?, bake_time_min=?,
           updated_at=datetime('now') WHERE id=?""",
        (data.name, data.description, data.category, data.default_height_cm,
         data.default_diameter_cm, data.prep_time_min, data.bake_time_min, layer_id)
    )
    await db.execute("DELETE FROM layer_ingredients WHERE layer_id=?", (layer_id,))
    await db.execute("DELETE FROM layer_steps WHERE layer_id=?", (layer_id,))
    await _insert_ingredients(db, layer_id, data.ingredients)
    await _insert_steps(db, layer_id, data.steps)
    await db.commit()
    return await _build_layer_out(db, await _fetch_layer(db, layer_id))


@router.post("/{layer_id}/clone", response_model=LayerOut, status_code=201)
async def clone_layer(layer_id: int, db=Depends(get_db)):
    original = await _fetch_layer(db, layer_id)
    ingredients = await _fetch_ingredients(db, layer_id)
    steps = await _fetch_steps(db, layer_id)

    cur = await db.execute(
        """INSERT INTO layers (name, description, category, default_height_cm,
           default_diameter_cm, prep_time_min, bake_time_min)
           VALUES (?,?,?,?,?,?,?)""",
        (original["name"] + " (kopia)", original["description"], original["category"],
         original["default_height_cm"], original["default_diameter_cm"],
         original["prep_time_min"], original["bake_time_min"])
    )
    new_id = cur.lastrowid
    await _insert_ingredients(db, new_id, ingredients)
    await _insert_steps(db, new_id, steps)
    await db.commit()
    return await _build_layer_out(db, await _fetch_layer(db, new_id))


@router.delete("/{layer_id}", status_code=204)
async def delete_layer(layer_id: int, db=Depends(get_db)):
    await _fetch_layer(db, layer_id)
    await db.execute("DELETE FROM layers WHERE id=?", (layer_id,))
    await db.commit()
