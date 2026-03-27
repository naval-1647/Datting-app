from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
import logging

from app.schemas.match import MatchResponse, MatchWithProfile
from app.services.match_service import MatchService
from app.models.user import UserInDB
from app.dependencies import get_current_user
from app.middleware import NotFoundException

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[MatchWithProfile])
async def get_matches(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get all matches for current user."""
    matches = await MatchService.get_user_matches(
        str(current_user.id),
        skip,
        limit
    )
    
    return matches


@router.get("/{match_id}", response_model=MatchWithProfile)
async def get_match(
    match_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get a specific match by ID."""
    match = await MatchService.get_match_by_id(match_id)
    
    if not match:
        raise NotFoundException("Match not found")
    
    # Verify user is part of this match
    if match["user1_id"] != str(current_user.id) and match["user2_id"] != str(current_user.id):
        raise NotFoundException("Match not found")
    
    return match


@router.delete("/{match_id}")
async def delete_match(
    match_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Unmatch/delete a match."""
    match = await MatchService.get_match_by_id(match_id)
    
    if not match:
        raise NotFoundException("Match not found")
    
    # Verify user is part of this match
    if match["user1_id"] != str(current_user.id) and match["user2_id"] != str(current_user.id):
        raise NotFoundException("Match not found")
    
    success = await MatchService.delete_match(match_id)
    
    if success:
        return {"success": True, "message": "Match deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete match")
