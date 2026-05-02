from typing import Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query

from app.db.queries import get_all_signals, get_signal_by_id

router = APIRouter(prefix="/api/signals", tags=["signals"])


@router.get("")
async def list_signals(
    sentiment: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    signal_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
):
    signals = await get_all_signals(
        sentiment_filter=sentiment,
        region_filter=region,
        type_filter=signal_type,
        limit=limit,
        skip=skip,
    )
    return signals


@router.get("/{signal_id}")
async def get_signal(signal_id: str):
    signal = await get_signal_by_id(signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return signal


@router.post("/refresh")
async def refresh_signals(background_tasks: BackgroundTasks, force: bool = False):
    from app.main import run_refresh, refresh_state
    from app.db.mongo import get_db
    if refresh_state["running"]:
        return {"status": "already_running"}
    if force:
        # Clear processed cache so all recent articles are re-classified
        await get_db()["processed_articles"].delete_many({})
    background_tasks.add_task(run_refresh)
    return {"status": "started", "force": force}
