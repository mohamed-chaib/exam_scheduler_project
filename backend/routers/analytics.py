from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import   database
from ..controllers import analytics
from ..models import DepartmentValidation, GlobalValidation, Departement
from ..schemas import ValidationUpdate

router = APIRouter(tags =['analytics'],prefix='/analytics')

@router.get("/validation/status")
def get_validation_summary(db: Session = Depends(database.get_db)):
    # Get all departments
    depts = db.query(Departement).all()
    summary = []
    
    for dept in depts:
        val = db.query(DepartmentValidation).filter(DepartmentValidation.dept_id == dept.id).first()
        status = val.status if val else "Pending"
        summary.append({
            "department": dept.nom,
            "status": status
        })
    return summary

@router.get("/validation/global")
def get_global_validation(db: Session = Depends(database.get_db)):
    val = db.query(GlobalValidation).first()
    return {"status": val.status if val else "Pending"}

@router.post("/validation/global")
def set_global_validation(update: ValidationUpdate, db: Session = Depends(database.get_db)):
    val = db.query(GlobalValidation).first()
    if not val:
        val = GlobalValidation(status=update.status)
        db.add(val)
    else:
        val.status = update.status
    db.commit()
    return {"status": val.status}
@router.get('/room_usage')
def get_room_usage(db:Session = Depends(database.get_db)):
    return analytics.get_rooms_usage_stats(db)

@router.get('/department_conflicts')
def get_department_conflicts(db:Session = Depends(database.get_db)):
    return analytics.get_department_stats(db)

@router.get('/professor_workload')
def get_professor_workload(db:Session = Depends(database.get_db)):
    return analytics.get_professor_workload_stats(db)