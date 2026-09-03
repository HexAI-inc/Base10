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


def _get_owned_material(db: Session, material_id: int, user: User) -> ClassroomMaterial:
    material = db.query(ClassroomMaterial).filter(ClassroomMaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    classroom = db.query(Classroom).filter(Classroom.id == material.classroom_id).first()
    if classroom.teacher_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only the teacher can modify this material")

    return material


@router.put("/materials/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: int,
    material_data: MaterialUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update classroom material (Teacher only)."""
    material = _get_owned_material(db, material_id, user)

    update_data = material_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(material, field, value)

    db.commit()
    db.refresh(material)

    return material


@router.delete("/materials/{material_id}")
async def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete classroom material (Teacher only)."""
    material = _get_owned_material(db, material_id, user)

    db.delete(material)
    db.commit()

    return {"message": "Material deleted successfully"}
