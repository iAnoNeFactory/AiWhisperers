from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from models import DecorationIn, DecorationOut

router = APIRouter()


@router.get("", response_model=list[DecorationOut])
async def list_decorations(db=Depends(get_db)):
    cur = await db.execute("SELECT * FROM decorations ORDER BY type, name")
    return [dict(r) for r in await cur.fetchall()]


@router.get("/{dec_id}", response_model=DecorationOut)
async def get_decoration(dec_id: int, db=Depends(get_db)):
    cur = await db.execute("SELECT * FROM decorations WHERE id=?", (dec_id,))
    row = await cur.fetchone()
    if not row:
        raise HTTPException(404, "Ozdoba nie istnieje")
    return dict(row)


@router.post("", response_model=DecorationOut, status_code=201)
async def create_decoration(data: DecorationIn, db=Depends(get_db)):
    cur = await db.execute(
        "INSERT INTO decorations (name, type, description, unit) VALUES (?,?,?,?)",
        (data.name, data.type, data.description, data.unit)
    )
    await db.commit()
    dec_id = cur.lastrowid
    cur2 = await db.execute("SELECT * FROM decorations WHERE id=?", (dec_id,))
    return dict(await cur2.fetchone())


@router.put("/{dec_id}", response_model=DecorationOut)
async def update_decoration(dec_id: int, data: DecorationIn, db=Depends(get_db)):
    cur = await db.execute("SELECT id FROM decorations WHERE id=?", (dec_id,))
    if not await cur.fetchone():
        raise HTTPException(404, "Ozdoba nie istnieje")
    await db.execute(
        "UPDATE decorations SET name=?, type=?, description=?, unit=? WHERE id=?",
        (data.name, data.type, data.description, data.unit, dec_id)
    )
    await db.commit()
    cur2 = await db.execute("SELECT * FROM decorations WHERE id=?", (dec_id,))
    return dict(await cur2.fetchone())


@router.delete("/{dec_id}", status_code=204)
async def delete_decoration(dec_id: int, db=Depends(get_db)):
    cur = await db.execute("SELECT id FROM decorations WHERE id=?", (dec_id,))
    if not await cur.fetchone():
        raise HTTPException(404, "Ozdoba nie istnieje")
    await db.execute("DELETE FROM decorations WHERE id=?", (dec_id,))
    await db.commit()
