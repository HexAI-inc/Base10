"""Classroom materials endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.classroom import Classroom, ClassroomMaterial
from app.models.user import User
from app.models.enums import UserRole
from app.core.security import get_current_user
from app.schemas.schemas import MaterialCreate, MaterialResponse, MaterialUpdate

router = APIRouter()


@router.get("/{classroom_id}/materials", response_model=List[MaterialResponse])
async def get_classroom_materials(classroom_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get all materials in a classroom."""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    materials = db.query(ClassroomMaterial).filter(
        ClassroomMaterial.classroom_id == classroom_id
    ).all()
    
    return materials


@router.post("/{classroom_id}/materials", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
async def create_material(
    classroom_id: int, 
    material_data: MaterialCreate, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    """Add material to a classroom (Teacher only)."""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    if classroom.teacher_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only the teacher can add materials")
    
    new_material = ClassroomMaterial(
        classroom_id=classroom_id,
        uploaded_by_id=user.id,
        title=material_data.title,
        description=material_data.description,
        asset_id=material_data.asset_id
    )
    
    db.add(new_material)
    db.commit()
    db.refresh(new_material)
    
    return new_material
