from backend.database import SessionLocal
from backend.models import DepartmentValidation, GlobalValidation, Departement, User

def debug_state():
    db = SessionLocal()
    try:
        print("=== DEBUGGING VISIBILITY STATE ===")
        
        # 1. Global Status
        g = db.query(GlobalValidation).first()
        g_status = g.status if g else "None"
        print(f"Global Status (Dean): '{g_status}'")
        
        # 2. Departments
        depts = db.query(Departement).all()
        print(f"\nFound {len(depts)} Departments:")
        
        for d in depts:
            val = db.query(DepartmentValidation).filter(DepartmentValidation.dept_id == d.id).first()
            val_status = val.status if val else "None"
            print(f" - ID {d.id} | Name: '{d.nom}' | Validation Status: '{val_status}'")
            
        print("\n=== LOGIC CHECK ===")
        print(f"Logic: Student View requires Global='Finalized' AND Dept='Validate'")
        
        if g_status != "Finalized":
            print("RESULT: All Students should be BLOCKED (Global not Finalized)")
        else:
            print("RESULT: Global is Finalized. Checking individual departments...")
            validated_ids = [d.id for d in depts if 
                             db.query(DepartmentValidation).filter(DepartmentValidation.dept_id == d.id).first() 
                             and db.query(DepartmentValidation).filter(DepartmentValidation.dept_id == d.id).first().status == "Validate"]
            
            if not validated_ids:
                print(" -> No departments are validated. All students blocked.")
            else:
                print(f" -> Students in Dept IDs {validated_ids} should have access.")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_state()
