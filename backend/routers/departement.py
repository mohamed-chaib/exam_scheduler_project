from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models
from .. import schemas , database
router = APIRouter(tags =['departments'],prefix='/departments')
@router.get('/')
def get_all_depatments(db:Session = Depends(database.get_db)):
    departments = db.query(models.Departement).all()
    return departments

@router.get('/{id}')
def get_depatment(id :int,db:Session = Depends(database.get_db)):
    department = db.query(models.Departement).filter(models.Departement.id == id).first()
    return department

@router.get("/{dept_id}/validation")
def get_validation_status(dept_id: int, db: Session = Depends(database.get_db)):
    val = db.query(models.DepartmentValidation).filter(models.DepartmentValidation.dept_id == dept_id).first()
    if not val:
        return {"status": "Pending"}
    return {"status": val.status}

@router.post("/{dept_id}/validation")
def set_validation_status(dept_id: int, update: schemas.ValidationUpdate, db: Session = Depends(database.get_db)):
    val = db.query(models.DepartmentValidation).filter(models.DepartmentValidation.dept_id == dept_id).first()
    if not val:
        val = models.DepartmentValidation(dept_id=dept_id, status=update.status)
        db.add(val)
    else:
        val.status = update.status
    db.commit()
    return {"status": "Updated", "new_status": val.status}