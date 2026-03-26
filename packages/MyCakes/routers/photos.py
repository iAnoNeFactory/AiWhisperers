import time
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from database import get_db

router = APIRouter()

PHOTOS_DIR = Path(__file__).parent.parent / "static" / "photos"
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
VALID_TARGETS = {"cakes", "layers", "frostings", "decorations"}


@router.post("/{target_type}/{target_id}")
async def upload_photo(
    target_type: str,
    target_id: int,
    file: UploadFile = File(...),
    db=Depends(get_db),
):
    if target_type not in VALID_TARGETS:
        raise HTTPException(400, f"target_type musi być jednym z: {VALID_TARGETS}")
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Dozwolone formaty: JPEG, PNG, WebP")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
    filename = f"{target_type[:-1]}_{target_id}_{int(time.time())}.{ext}"
    dest_dir = PHOTOS_DIR / target_type
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / filename

    content = await file.read()
    dest.write_bytes(content)

    # Strip trailing 's' to get singular table name (cakes→cake, layers→layer...)
    table = target_type.rstrip("s") + "s"
    photo_url = f"/photos/{target_type}/{filename}"

    await db.execute(f"UPDATE {table} SET photo_path=? WHERE id=?", (photo_url, target_id))
    await db.commit()

    return {"photo_path": photo_url}
