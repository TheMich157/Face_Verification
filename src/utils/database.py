from sqlalchemy import create_engine, Column, Integer, String, DateTime, LargeBinary, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Verification(Base):
    __tablename__ = 'verifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    username = Column(String, nullable=False)
    submission_date = Column(DateTime, default=datetime.utcnow)
    media_data = Column(LargeBinary, nullable=False)
    media_type = Column(String, nullable=False)  # 'photo' or 'video'
    estimated_age = Column(Float)
    verified = Column(Boolean, default=False)
    reviewed = Column(Boolean, default=False)
    reviewer_id = Column(String, nullable=True)
    review_date = Column(DateTime, nullable=True)
    review_notes = Column(String, nullable=True)

class Database:
    def __init__(self):
        self.engine = create_engine('sqlite:///verification_data.db')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_verification(self, user_id, username, media_data, media_type, estimated_age):
        """Add a new verification entry"""
        verification = Verification(
            user_id=user_id,
            username=username,
            media_data=media_data,
            media_type=media_type,
            estimated_age=estimated_age
        )
        self.session.add(verification)
        self.session.commit()
        return verification.id

    def get_pending_reviews(self):
        """Get all unreviewed verifications"""
        return self.session.query(Verification).filter_by(reviewed=False).all()

    def get_verification(self, verification_id):
        """Get a specific verification entry"""
        return self.session.query(Verification).filter_by(id=verification_id).first()

    def update_review(self, verification_id, reviewer_id, verified, notes=None):
        """Update verification review status"""
        verification = self.get_verification(verification_id)
        if verification:
            verification.reviewed = True
            verification.reviewer_id = reviewer_id
            verification.verified = verified
            verification.review_date = datetime.utcnow()
            verification.review_notes = notes
            self.session.commit()
            return True
        return False

    def get_user_verifications(self, user_id):
        """Get all verifications for a specific user"""
        return self.session.query(Verification).filter_by(user_id=user_id).all()

    def cleanup_old_verifications(self, days=30):
        """Remove verification entries older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        self.session.query(Verification).filter(
            Verification.submission_date < cutoff_date,
            Verification.reviewed == True
        ).delete()
        self.session.commit()
