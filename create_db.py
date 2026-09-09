#בס"ד
import enum
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base

# 1. הגדרת הבסיס של SQLAlchemy
Base = declarative_base()

# 2. הגדרת הסטטוסים של ההזמנה במערכת FORCED
class BookingStatus(enum.Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    MATCHING = "MATCHING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DISPUTED = "DISPUTED"

# 3. טבלת בעלי מקצוע
class Provider(Base):
    __tablename__ = "providers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String, unique=True, nullable=False)
    
    # פיצול השמות עבור בעל המקצוע
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    
    profession = Column(String, nullable=False)
    is_available = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # קשר לפייתון: גישה קלה לכל ההזמנות ששויכו לבעל מקצוע זה
    bookings = relationship("Booking", back_populates="provider")

# 4. טבלת לקוחות אורחים
class GuestClient(Base):
    __tablename__ = "guest_clients"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String, nullable=False)
    
    # הוספת שם פרטי ושם משפחה גם לאורח (ייקלטו ברגע ביצוע ההזמנה)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # קשר לפייתון: גישה קלה לכל ההזמנות שפתח האורח הזה
    bookings = relationship("Booking", back_populates="guest_client")

# 5. טבלת ניהול ההזמנות
class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # מפתחות זרים - החיבור הפיזי ב-DB ללקוח ולבעל המקצוע
    guest_client_id = Column(String, ForeignKey("guest_clients.id"), nullable=False)
    provider_id = Column(String, ForeignKey("providers.id"), nullable=True)
    
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING_PAYMENT)
    address = Column(String, nullable=False)
    description = Column(String, nullable=False)
    deposit_amount = Column(Float, nullable=False)
    payment_intent_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # קשרים דו-כיווניים של פייתון לניווט קל בין הישויות בקוד
    guest_client = relationship("GuestClient", back_populates="bookings")
    provider = relationship("Provider", back_populates="bookings")
    messages = relationship("ChatMessage", back_populates="booking")

# 6. טבלת הודעות צ'אט מוגנות
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # מפתח זר - מקשר את הודעת הטקסט ישירות לחלון ההזמנה הספציפי
    booking_id = Column(String, ForeignKey("bookings.id"), nullable=False)
    
    sender_type = Column(String, nullable=False)  # שומר "GUEST" או "PROVIDER"
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # קשר לפייתון: גישה חזרה לפרטי ההזמנה מתוך ההודעה
    booking = relationship("Booking", back_populates="messages")
    
class ForcedFavoriteProvider(Base):
    __tablename__ = "favorite_providers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    guest_client_id = Column(String, ForeignKey("guest_clients.id"), nullable=False)
    provider_id = Column(String, ForeignKey("providers.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ========================================================
# 🔥 יצירת קובץ בסיס הנתונים המקומי forced.db בפועל 🔥
# ========================================================

# הגדרת שם הקובץ שיווצר פיזית בתיקייה שלך
DATABASE_URL = "sqlite:///./forced.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

if __name__ == "__main__":
    print("מריץ את פקודת היצירה עבור מערכת FORCED...")
    
    # פקודה הסורקת את ה-Classes ומקימה את קובץ ה-forced.db
    Base.metadata.create_all(bind=engine)
    
    print("הצלחה! נוצר קובץ חדש בשם forced.db המכיל את כל טבלאות ה-MVP המעודכנות")
#שכוייח גדול לך ולבינה המלאכותית שלך!