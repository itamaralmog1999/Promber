#בס"ד
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker, Session
# מייבאים את ה-engine ואת המודל שכתבת בקוד הקודם
from create_db import engine, GuestClient 

# 1. יצירת חיבור (Session) לבסיס הנתונים
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. יצירת אפליקציית ה-FastAPI
app = FastAPI(title="FORCED API System")

# פונקציית עזר לפתיחה וסגירה אוטומטית של חיבור ל-DB בכל בקשה
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 3. הגדרת "סכימה" של Pydantic - זה מגדיר איזה מידע ה-API מצפה לקבל מהמשתמש
class GuestCreateSchema(BaseModel):
    phone: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True

# ========================================================
# 🔥 נקודות הקצה של ה-API (Endpoints) 🔥
# ========================================================

# בקשת POST: יצירת לקוח אורח חדש במערכת
@app.post("/guests/", response_model=GuestCreateSchema)
def create_guest(guest_data: GuestCreateSchema, db: Session = Depends(get_db)):
    # יצירת אובייקט חדש לפי המודל של SQLAlchemy
    new_guest = GuestClient(
        phone=guest_data.phone,
        first_name=guest_data.first_name,
        last_name=guest_data.last_name
    )
    # שמירה בבסיס הנתונים
    db.add(new_guest)
    db.commit()
    db.refresh(new_guest)
    return new_guest

# בקשת GET: שליפת כל הלקוחות האורחים הקיימים במערכת
@app.get("/guests/")
def get_all_guests(db: Session = Depends(get_db)):
    guests = db.query(GuestClient).all()
    return guests
