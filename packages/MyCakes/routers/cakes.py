from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from models import (
    CakeIn, CakeOut, CakeSummary,
    CakeLayerIn, CakeLayerOut,
    CakeFrostingIn, CakeFrostingOut,
    CakeDecorationIn, CakeDecorationOut,
)

router = APIRouter()


async def _fetch_cake(db, cake_id: int) -> dict:
    cur = await db.execute("SELECT * FROM cakes WHERE id=?", (cake_id,))
    row = await cur.fetchone()
    if not row:
        raise HTTPException(404, "Tort nie istnieje")
    return dict(row)


async def _fetch_cake_layers(db, cake_id: int) -> list[CakeLayerOut]:
    cur = await db.execute(
        """SELECT cl.*, l.name AS layer_name, l.category AS layer_category,
                  l.default_height_cm, l.default_diameter_cm
           FROM cake_layers cl
           JOIN layers l ON cl.layer_id = l.id
           WHERE cl.cake_id = ?
           ORDER BY cl.position, cl.id""",
        (cake_id,)
    )
    rows = [dict(r) for r in await cur.fetchall()]
    result = []
    for r in rows:
        # Use override height/diameter or layer defaults
        h = r["height_cm"] if r["height_cm"] is not None else r["default_height_cm"]
        d = r["diameter_cm"] if r["diameter_cm"] is not None else r["default_diameter_cm"]
        ing_cur = await db.execute(
            "SELECT * FROM layer_ingredients WHERE layer_id=? ORDER BY id", (r["layer_id"],)
        )
        ingredients = [dict(i) for i in await ing_cur.fetchall()]
        result.append(CakeLayerOut(
            id=r["id"],
            layer_id=r["layer_id"],
            layer_name=r["layer_name"],
            layer_category=r["layer_category"],
            position=r["position"],
            height_cm=h,
            diameter_cm=d,
            ingredients=ingredients,
        ))
    return result


async def _fetch_cake_frostings(db, cake_id: int) -> list[CakeFrostingOut]:
    cur = await db.execute(
        """SELECT cf.*, f.name AS frosting_name, f.type AS frosting_type
           FROM cake_frostings cf
           JOIN frostings f ON cf.frosting_id = f.id
           WHERE cf.cake_id = ?""",
        (cake_id,)
    )
    rows = [dict(r) for r in await cur.fetchall()]
    result = []
    for r in rows:
        ing_cur = await db.execute(
            "SELECT * FROM frosting_ingredients WHERE frosting_id=? ORDER BY id", (r["frosting_id"],)
        )
        ingredients = [dict(i) for i in await ing_cur.fetchall()]
        result.append(CakeFrostingOut(
            id=r["id"],
            frosting_id=r["frosting_id"],
            frosting_name=r["frosting_name"],
            frosting_type=r["frosting_type"],
            apply_top=bool(r["apply_top"]),
            apply_sides=bool(r["apply_sides"]),
            ingredients=ingredients,
        ))
    return result


async def _fetch_cake_decorations(db, cake_id: int) -> list[CakeDecorationOut]:
    cur = await db.execute(
        """SELECT cd.*, d.name AS decoration_name, d.type AS decoration_type
           FROM cake_decorations cd
           JOIN decorations d ON cd.decoration_id = d.id
           WHERE cd.cake_id = ?""",
        (cake_id,)
    )
    rows = [dict(r) for r in await cur.fetchall()]
    return [CakeDecorationOut(
        id=r["id"],
        decoration_id=r["decoration_id"],
        decoration_name=r["decoration_name"],
        decoration_type=r["decoration_type"],
        quantity=r["quantity"],
        note=r["note"],
    ) for r in rows]


async def _rating(db, cake_id: int) -> tuple:
    cur = await db.execute(
        "SELECT AVG(rating), COUNT(*) FROM reviews WHERE target_type='cake' AND target_id=?",
        (cake_id,)
    )
    row = await cur.fetchone()
    avg = round(row[0], 1) if row[0] else None
    return avg, row[1]


async def _build_cake_out(db, cake: dict) -> CakeOut:
    layers = await _fetch_cake_layers(db, cake["id"])
    frostings = await _fetch_cake_frostings(db, cake["id"])
    decorations = await _fetch_cake_decorations(db, cake["id"])
    avg, cnt = await _rating(db, cake["id"])
    total_h = sum(l.height_cm for l in layers)
    return CakeOut(
        **cake,
        layers=layers,
        frostings=frostings,
        decorations=decorations,
        total_height_cm=total_h,
        avg_rating=avg,
        review_count=cnt,
    )


# ── Cake CRUD ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[CakeSummary])
async def list_cakes(db=Depends(get_db)):
    cur = await db.execute("SELECT * FROM cakes ORDER BY updated_at DESC")
    cakes = [dict(r) for r in await cur.fetchall()]
    result = []
    for c in cakes:
        layers = await _fetch_cake_layers(db, c["id"])
        avg, cnt = await _rating(db, c["id"])
        total_h = sum(l.height_cm for l in layers)
        result.append(CakeSummary(
            **c,
            total_height_cm=total_h,
            layer_count=len(layers),
            avg_rating=avg,
            review_count=cnt,
        ))
    return result


@router.get("/{cake_id}", response_model=CakeOut)
async def get_cake(cake_id: int, db=Depends(get_db)):
    cake = await _fetch_cake(db, cake_id)
    return await _build_cake_out(db, cake)


@router.post("", response_model=CakeOut, status_code=201)
async def create_cake(data: CakeIn, db=Depends(get_db)):
    cur = await db.execute(
        "INSERT INTO cakes (name, description, diameter_cm, serves) VALUES (?,?,?,?)",
        (data.name, data.description, data.diameter_cm, data.serves)
    )
    await db.commit()
    cake = await _fetch_cake(db, cur.lastrowid)
    return await _build_cake_out(db, cake)


@router.put("/{cake_id}", response_model=CakeOut)
async def update_cake(cake_id: int, data: CakeIn, db=Depends(get_db)):
    await _fetch_cake(db, cake_id)
    await db.execute(
        "UPDATE cakes SET name=?, description=?, diameter_cm=?, serves=?, updated_at=datetime('now') WHERE id=?",
        (data.name, data.description, data.diameter_cm, data.serves, cake_id)
    )
    await db.commit()
    return await _build_cake_out(db, await _fetch_cake(db, cake_id))


@router.post("/{cake_id}/clone", response_model=CakeOut, status_code=201)
async def clone_cake(cake_id: int, db=Depends(get_db)):
    original = await _fetch_cake(db, cake_id)
    cur = await db.execute(
        "INSERT INTO cakes (name, description, diameter_cm, serves) VALUES (?,?,?,?)",
        (original["name"] + " (kopia)", original["description"],
         original["diameter_cm"], original.get("serves", 0))
    )
    new_id = cur.lastrowid

    # Copy layers
    layers_cur = await db.execute("SELECT * FROM cake_layers WHERE cake_id=?", (cake_id,))
    for r in await layers_cur.fetchall():
        await db.execute(
            "INSERT INTO cake_layers (cake_id, layer_id, position, height_cm, diameter_cm) VALUES (?,?,?,?,?)",
            (new_id, r["layer_id"], r["position"], r["height_cm"], r["diameter_cm"])
        )

    # Copy frostings
    frost_cur = await db.execute("SELECT * FROM cake_frostings WHERE cake_id=?", (cake_id,))
    for r in await frost_cur.fetchall():
        await db.execute(
            "INSERT INTO cake_frostings (cake_id, frosting_id, apply_top, apply_sides) VALUES (?,?,?,?)",
            (new_id, r["frosting_id"], r["apply_top"], r["apply_sides"])
        )

    # Copy decorations
    deco_cur = await db.execute("SELECT * FROM cake_decorations WHERE cake_id=?", (cake_id,))
    for r in await deco_cur.fetchall():
        await db.execute(
            "INSERT INTO cake_decorations (cake_id, decoration_id, quantity, note) VALUES (?,?,?,?)",
            (new_id, r["decoration_id"], r["quantity"], r["note"])
        )

    await db.commit()
    return await _build_cake_out(db, await _fetch_cake(db, new_id))


@router.delete("/{cake_id}", status_code=204)
async def delete_cake(cake_id: int, db=Depends(get_db)):
    await _fetch_cake(db, cake_id)
    await db.execute("DELETE FROM cakes WHERE id=?", (cake_id,))
    await db.commit()


# ── Cake Layers ───────────────────────────────────────────────────────────────

@router.post("/{cake_id}/layers", response_model=CakeOut, status_code=201)
async def add_layer(cake_id: int, data: CakeLayerIn, db=Depends(get_db)):
    await _fetch_cake(db, cake_id)
    cur = await db.execute("SELECT id FROM layers WHERE id=?", (data.layer_id,))
    if not await cur.fetchone():
        raise HTTPException(404, "Warstwa nie istnieje")
    await db.execute(
        "INSERT INTO cake_layers (cake_id, layer_id, position, height_cm, diameter_cm) VALUES (?,?,?,?,?)",
        (cake_id, data.layer_id, data.position, data.height_cm, data.diameter_cm)
    )
    await db.execute("UPDATE cakes SET updated_at=datetime('now') WHERE id=?", (cake_id,))
    await db.commit()
    return await _build_cake_out(db, await _fetch_cake(db, cake_id))


@router.put("/{cake_id}/layers/{cl_id}", response_model=CakeOut)
async def update_cake_layer(cake_id: int, cl_id: int, data: CakeLayerIn, db=Depends(get_db)):
    cur = await db.execute("SELECT id FROM cake_layers WHERE id=? AND cake_id=?", (cl_id, cake_id))
    if not await cur.fetchone():
        raise HTTPException(404, "Warstwa tortu nie istnieje")
    await db.execute(
        "UPDATE cake_layers SET layer_id=?, position=?, height_cm=?, diameter_cm=? WHERE id=?",
        (data.layer_id, data.position, data.height_cm, data.diameter_cm, cl_id)
    )
    await db.execute("UPDATE cakes SET updated_at=datetime('now') WHERE id=?", (cake_id,))
    await db.commit()
    return await _build_cake_out(db, await _fetch_cake(db, cake_id))


@router.delete("/{cake_id}/layers/{cl_id}", response_model=CakeOut)
async def remove_layer(cake_id: int, cl_id: int, db=Depends(get_db)):
    cur = await db.execute("SELECT id FROM cake_layers WHERE id=? AND cake_id=?", (cl_id, cake_id))
    if not await cur.fetchone():
        raise HTTPException(404, "Warstwa tortu nie istnieje")
    await db.execute("DELETE FROM cake_layers WHERE id=?", (cl_id,))
    await db.execute("UPDATE cakes SET updated_at=datetime('now') WHERE id=?", (cake_id,))
    await db.commit()
    return await _build_cake_out(db, await _fetch_cake(db, cake_id))


# ── Cake Frostings ────────────────────────────────────────────────────────────

@router.post("/{cake_id}/frostings", response_model=CakeOut, status_code=201)
async def add_frosting(cake_id: int, data: CakeFrostingIn, db=Depends(get_db)):
    await _fetch_cake(db, cake_id)
    cur = await db.execute("SELECT id FROM frostings WHERE id=?", (data.frosting_id,))
    if not await cur.fetchone():
        raise HTTPException(404, "Tynk nie istnieje")
    await db.execute(
        "INSERT INTO cake_frostings (cake_id, frosting_id, apply_top, apply_sides) VALUES (?,?,?,?)",
        (cake_id, data.frosting_id, int(data.apply_top), int(data.apply_sides))
    )
    await db.execute("UPDATE cakes SET updated_at=datetime('now') WHERE id=?", (cake_id,))
    await db.commit()
    return await _build_cake_out(db, await _fetch_cake(db, cake_id))


@router.delete("/{cake_id}/frostings/{cf_id}", response_model=CakeOut)
async def remove_frosting(cake_id: int, cf_id: int, db=Depends(get_db)):
    cur = await db.execute("SELECT id FROM cake_frostings WHERE id=? AND cake_id=?", (cf_id, cake_id))
    if not await cur.fetchone():
        raise HTTPException(404, "Tynk tortu nie istnieje")
    await db.execute("DELETE FROM cake_frostings WHERE id=?", (cf_id,))
    await db.execute("UPDATE cakes SET updated_at=datetime('now') WHERE id=?", (cake_id,))
    await db.commit()
    return await _build_cake_out(db, await _fetch_cake(db, cake_id))


# ── Cake Decorations ──────────────────────────────────────────────────────────

@router.post("/{cake_id}/decorations", response_model=CakeOut, status_code=201)
async def add_decoration(cake_id: int, data: CakeDecorationIn, db=Depends(get_db)):
    await _fetch_cake(db, cake_id)
    cur = await db.execute("SELECT id FROM decorations WHERE id=?", (data.decoration_id,))
    if not await cur.fetchone():
        raise HTTPException(404, "Ozdoba nie istnieje")
    await db.execute(
        "INSERT INTO cake_decorations (cake_id, decoration_id, quantity, note) VALUES (?,?,?,?)",
        (cake_id, data.decoration_id, data.quantity, data.note)
    )
    await db.execute("UPDATE cakes SET updated_at=datetime('now') WHERE id=?", (cake_id,))
    await db.commit()
    return await _build_cake_out(db, await _fetch_cake(db, cake_id))


@router.delete("/{cake_id}/decorations/{cd_id}", response_model=CakeOut)
async def remove_decoration(cake_id: int, cd_id: int, db=Depends(get_db)):
    cur = await db.execute("SELECT id FROM cake_decorations WHERE id=? AND cake_id=?", (cd_id, cake_id))
    if not await cur.fetchone():
        raise HTTPException(404, "Ozdoba tortu nie istnieje")
    await db.execute("DELETE FROM cake_decorations WHERE id=?", (cd_id,))
    await db.execute("UPDATE cakes SET updated_at=datetime('now') WHERE id=?", (cake_id,))
    await db.commit()
    return await _build_cake_out(db, await _fetch_cake(db, cake_id))
