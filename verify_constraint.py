import sys
import os
from datetime import datetime
from collections import defaultdict

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SessionLocal
from backend.controllers.exam import generate_smart_exam_schedule
from backend.models import Examen, Module

def verify_schedule():
    db = SessionLocal()
    try:
        print("Generaring new schedule...")
        # Generate schedule starting from tomorrow
        start_date = datetime.now().strftime("%Y-%m-%d")
        result = generate_smart_exam_schedule(db, start_date)
        
        if result.get("status") != "Success":
            print(f"Generation failed: {result}")
            return

        print(f"Generation complete. Exams created: {result.get('exams_count')}")
        
        # Verify constraints
        exams = db.query(Examen).all()
        
        # formations[date] = list of formation_ids
        formation_dates = defaultdict(list)
        
        violations = 0
        
        for exam in exams:
            # We need to get the formation_id for each exam
            # Examen -> Module -> Formation
            # Loading relationship might require joinedload or accessing property
            module = db.query(Module).filter(Module.id == exam.module_id).first()
            if not module:
                continue
                
            fmt_id = module.formation_id
            date_str = exam.date_heure.strftime("%Y-%m-%d")
            
            formation_dates[(fmt_id, date_str)].append(exam.id)
            
        for (fmt_id, date_str), exam_ids in formation_dates.items():
            if len(exam_ids) > 1:
                print(f"[VIOLATION] Formation {fmt_id} has {len(exam_ids)} exams on {date_str}: IDs {exam_ids}")
                violations += 1
                
        if violations == 0:
            print("✅ SUCCESS: No formation has more than one exam per day.")
        else:
            print(f"❌ FAILED: Found {violations} violations.")
            
    finally:
        db.close()

if __name__ == "__main__":
    verify_schedule()
