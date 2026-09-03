from fastapi import APIRouter
from app.api.v1.classrooms import base, stream, members, materials, assignments, submissions, ai, profiles

router = APIRouter()

router.include_router(base.router, prefix="/classrooms", tags=["Classrooms"])
router.include_router(stream.router, prefix="/classrooms", tags=["Classroom Stream"])
router.include_router(members.router, prefix="/classrooms", tags=["Classroom Members"])
router.include_router(materials.router, prefix="/classrooms", tags=["Classroom Materials"])
router.include_router(assignments.router, prefix="/classrooms", tags=["Classroom Assignments"])
router.include_router(submissions.router, prefix="/classrooms", tags=["Classroom Submissions"])
router.include_router(ai.router, prefix="/classrooms", tags=["Classroom AI"])
router.include_router(profiles.router, prefix="/classrooms", tags=["Classroom Student Profiles"])
