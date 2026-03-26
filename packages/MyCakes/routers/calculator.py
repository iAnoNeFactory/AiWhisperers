import math
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from database import get_db
from models import CalcResult, CalcLayerResult, CalcFrostingResult

router = APIRouter()


@router.get("", response_model=CalcResult)
async def calculate(
    cake_id: int = Query(...),
    new_d: Optional[float] = Query(None, description="Nowa średnica tortu [cm]"),
    new_h: Optional[float] = Query(None, description="Nowa całkowita wysokość [cm] (opcjonalnie)"),
    target_serves: Optional[int] = Query(None, description="Docelowa liczba osób"),
    db=Depends(get_db),
):
    cur = await db.execute("SELECT * FROM cakes WHERE id=?", (cake_id,))
    cake = await cur.fetchone()
    if not cake:
        raise HTTPException(404, "Tort nie istnieje")
    cake = dict(cake)

    orig_d = cake["diameter_cm"]
    orig_serves = cake.get("serves") or 0

    # Resolve new_d: either direct or from target_serves
    if new_d is None and target_serves is not None:
        if orig_serves <= 0:
            raise HTTPException(400, "Tort nie ma podanej liczby osób — uzupełnij pole 'na ile osób' w edycji tortu")
        new_d = round(orig_d * math.sqrt(target_serves / orig_serves), 1)
    elif new_d is None:
        raise HTTPException(400, "Podaj new_d lub target_serves")

    # Fetch layers
    cur = await db.execute(
        """SELECT cl.*, l.name AS layer_name, l.default_height_cm, l.default_diameter_cm
           FROM cake_layers cl
           JOIN layers l ON cl.layer_id = l.id
           WHERE cl.cake_id = ?
           ORDER BY cl.position, cl.id""",
        (cake_id,)
    )
    cake_layers = [dict(r) for r in await cur.fetchall()]

    orig_total_h = sum(
        (r["height_cm"] if r["height_cm"] is not None else r["default_height_cm"])
        for r in cake_layers
    )

    h_scale = (new_h / orig_total_h) if (new_h and orig_total_h > 0) else 1.0
    new_total_h = new_h if new_h else orig_total_h

    layer_results = []
    for r in cake_layers:
        orig_layer_h = r["height_cm"] if r["height_cm"] is not None else r["default_height_cm"]
        orig_layer_d = r["diameter_cm"] if r["diameter_cm"] is not None else r["default_diameter_cm"]
        new_layer_h = orig_layer_h * h_scale
        new_layer_d = (orig_layer_d / orig_d) * new_d if orig_d > 0 else new_d
        vol_scale = (new_layer_d / orig_layer_d) ** 2 * (new_layer_h / orig_layer_h) \
                    if orig_layer_d > 0 and orig_layer_h > 0 else 1.0

        ing_cur = await db.execute(
            "SELECT * FROM layer_ingredients WHERE layer_id=?", (r["layer_id"],)
        )
        ingredients = []
        for ing in await ing_cur.fetchall():
            ing = dict(ing)
            ingredients.append({
                "name": ing["name"],
                "orig_amount": ing["amount"],
                "new_amount": round(ing["amount"] * vol_scale, 1),
                "unit": ing["unit"],
            })

        layer_results.append(CalcLayerResult(
            layer_id=r["layer_id"],
            layer_name=r["layer_name"],
            position=r["position"],
            orig_height_cm=round(orig_layer_h, 2),
            orig_diameter_cm=round(orig_layer_d, 2),
            new_height_cm=round(new_layer_h, 2),
            new_diameter_cm=round(new_layer_d, 2),
            volume_scale=round(vol_scale, 4),
            ingredients=ingredients,
        ))

    # Frostings — scale by surface area relative to frosting's own reference dimensions
    cur = await db.execute(
        """SELECT cf.*, f.name AS frosting_name, f.ref_diameter_cm, f.ref_height_cm,
                  cf.apply_top, cf.apply_sides
           FROM cake_frostings cf
           JOIN frostings f ON cf.frosting_id = f.id
           WHERE cf.cake_id = ?""",
        (cake_id,)
    )
    frosting_rows = [dict(r) for r in await cur.fetchall()]

    frosting_results = []
    for r in frosting_rows:
        ref_d = r.get("ref_diameter_cm") or 24.0
        ref_h = r.get("ref_height_cm") or 10.0

        ref_sides = math.pi * ref_d * ref_h if r["apply_sides"] else 0.0
        ref_top   = math.pi * (ref_d / 2) ** 2 if r["apply_top"] else 0.0
        ref_area  = ref_sides + ref_top

        new_sides = math.pi * new_d * new_total_h if r["apply_sides"] else 0.0
        new_top   = math.pi * (new_d / 2) ** 2   if r["apply_top"]   else 0.0
        new_area  = new_sides + new_top

        area_scale = (new_area / ref_area) if ref_area > 0 else 1.0

        ing_cur = await db.execute(
            "SELECT * FROM frosting_ingredients WHERE frosting_id=?", (r["frosting_id"],)
        )
        ingredients = []
        for ing in await ing_cur.fetchall():
            ing = dict(ing)
            ingredients.append({
                "name": ing["name"],
                "orig_amount": ing["amount"],
                "new_amount": round(ing["amount"] * area_scale, 1),
                "unit": ing["unit"],
            })

        frosting_results.append(CalcFrostingResult(
            frosting_id=r["frosting_id"],
            frosting_name=r["frosting_name"],
            ref_area_cm2=round(ref_area, 1),
            new_area_cm2=round(new_area, 1),
            area_scale=round(area_scale, 4),
            ingredients=ingredients,
        ))

    return CalcResult(
        cake_id=cake_id,
        cake_name=cake["name"],
        orig_diameter_cm=orig_d,
        new_diameter_cm=new_d,
        orig_total_height_cm=round(orig_total_h, 2),
        new_total_height_cm=round(new_total_h, 2),
        layers=layer_results,
        frostings=frosting_results,
    )
