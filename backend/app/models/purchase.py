"""
Purchase model and related enums
"""
from enum import Enum
from datetime import datetime
from sqlalchemy import Index

from .base import db, BaseModel


class ApprovalStatus(Enum):
    """Purchase approval status enumeration"""
    PENDING_SUBLEAD = 'Pending Sublead Approval'
    PENDING_EXECUTIVE = 'Pending Executive Approval'
    FULLY_APPROVED = 'Fully Approved'
    REJECTED = 'Rejected'
    
    @classmethod
    def get_choices(cls):
        """Get choices for forms"""
        return [(status.value, status.value) for status in cls]


class PurchaseStatus(Enum):
    """Purchase fulfillment status enumeration"""
    NOT_PURCHASED = 'Not Yet Purchased'
    PURCHASED = 'Purchased'
    SHIPPED = 'Shipped'
    ARRIVED = 'Arrived'
    CANCELLED = 'Cancelled'
    
    @classmethod
    def get_choices(cls):
        """Get choices for forms"""
        return [(status.value, status.value) for status in cls]


class UrgencyLevel(Enum):
    """Purchase urgency level enumeration"""
    NEITHER = 'Neither'
    URGENT = 'Urgent'
    SPECIAL_LARGE = 'Special/Large'
    BOTH = 'Both'
    
    @classmethod
    def get_choices(cls):
        """Get choices for forms"""
        return [(level.value, level.value) for level in cls]


class Purchase(BaseModel):
    """Purchase order model"""
    __tablename__ = 'purchases'
    
    # Item details
    item_name = db.Column(db.String(200), nullable=False)
    vendor_name = db.Column(db.String(200), nullable=False)
    item_link = db.Column(db.String(500))
    quantity = db.Column(db.Integer, default=1, nullable=False)
    
    # Pricing
    price = db.Column(db.Numeric(10, 2), nullable=False)
    shipping_cost = db.Column(db.Numeric(10, 2), default=0.0)
    
    # Organization
    subteam = db.Column(db.String(100), nullable=False)
    subproject = db.Column(db.String(200))
    purpose = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Requester info
    requester_name = db.Column(db.String(200), nullable=False)
    requester_email = db.Column(db.String(200), nullable=False)
    
    # Status tracking
    approval_status = db.Column(
        db.Enum(ApprovalStatus), 
        default=ApprovalStatus.PENDING_SUBLEAD, 
        nullable=False
    )
    status = db.Column(
        db.Enum(PurchaseStatus), 
        default=PurchaseStatus.NOT_PURCHASED, 
        nullable=False
    )
    urgency = db.Column(
        db.Enum(UrgencyLevel), 
        default=UrgencyLevel.NEITHER, 
        nullable=False
    )
    
    # Timestamps
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    shipped_at = db.Column(db.DateTime)
    arrived_at = db.Column(db.DateTime)
    
    # Approval tracking
    sublead_email = db.Column(db.String(120))
    exec_email = db.Column(db.String(120))
    exec_approval_status = db.Column(db.String(50), default='Pending')
    
    # File uploads
    arrival_photo = db.Column(db.String(200))
    
    # Soft delete and resolution
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False, nullable=False)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_purchase_status', 'status'),
        Index('idx_approval_status', 'approval_status'),
        Index('idx_user_id', 'user_id'),
        Index('idx_subteam', 'subteam'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f'<Purchase {self.item_name} - {self.status.value}>'
    
    @property
    def total_cost(self) -> float:
        """Calculate total cost including shipping"""
        return float(self.price) + float(self.shipping_cost or 0)
    
    @property
    def is_urgent(self) -> bool:
        """Check if purchase is urgent"""
        return self.urgency in [UrgencyLevel.URGENT, UrgencyLevel.BOTH]
    
    @property
    def is_special_large(self) -> bool:
        """Check if purchase is special/large"""
        return self.urgency in [UrgencyLevel.SPECIAL_LARGE, UrgencyLevel.BOTH]
    
    @property
    def needs_executive_approval(self) -> bool:
        """Check if purchase needs executive approval"""
        return self.is_urgent or self.is_special_large or self.total_cost > 3000
    
    @property
    def can_be_purchased(self) -> bool:
        """Check if purchase can be executed"""
        return self.approval_status == ApprovalStatus.FULLY_APPROVED
    
    @property
    def is_pending_approval(self) -> bool:
        """Check if purchase is pending any approval"""
        return self.approval_status in [
            ApprovalStatus.PENDING_SUBLEAD, 
            ApprovalStatus.PENDING_EXECUTIVE
        ]
    
    def approve_by_sublead(self, sublead_email: str) -> None:
        """Approve purchase by sublead"""
        self.sublead_email = sublead_email
        
        if self.needs_executive_approval:
            self.approval_status = ApprovalStatus.PENDING_EXECUTIVE
        else:
            self.approval_status = ApprovalStatus.FULLY_APPROVED
        
        db.session.commit()
    
    def approve_by_executive(self, exec_email: str) -> None:
        """Approve purchase by executive"""
        self.exec_email = exec_email
        self.exec_approval_status = 'Approved'
        self.approval_status = ApprovalStatus.FULLY_APPROVED
        db.session.commit()
    
    def reject(self, reason: str = None) -> None:
        """Reject purchase"""
        self.approval_status = ApprovalStatus.REJECTED
        if reason:
            self.notes = f"{self.notes or ''}\n\nRejection reason: {reason}".strip()
        db.session.commit()
    
    def mark_as_purchased(self) -> None:
        """Mark purchase as purchased"""
        if not self.can_be_purchased:
            raise ValueError("Purchase must be fully approved before marking as purchased")
        
        self.status = PurchaseStatus.PURCHASED
        db.session.commit()
    
    def mark_as_shipped(self) -> None:
        """Mark purchase as shipped"""
        if self.status != PurchaseStatus.PURCHASED:
            raise ValueError("Purchase must be purchased before marking as shipped")
        
        self.status = PurchaseStatus.SHIPPED
        self.shipped_at = datetime.utcnow()
        db.session.commit()
    
    def mark_as_arrived(self, photo_filename: str = None) -> None:
        """Mark purchase as arrived"""
        if self.status != PurchaseStatus.SHIPPED:
            raise ValueError("Purchase must be shipped before marking as arrived")
        
        self.status = PurchaseStatus.ARRIVED
        self.arrived_at = datetime.utcnow()
        if photo_filename:
            self.arrival_photo = photo_filename
        db.session.commit()
    
    def soft_delete(self) -> None:
        """Soft delete the purchase"""
        self.is_deleted = True
        db.session.commit()
    
    def restore(self) -> None:
        """Restore soft deleted purchase"""
        self.is_deleted = False
        db.session.commit()
    
    def resolve(self) -> None:
        """Mark purchase as resolved"""
        self.is_resolved = True
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        data = super().to_dict()
        data.update({
            'approval_status': self.approval_status.value if self.approval_status else None,
            'status': self.status.value if self.status else None,
            'urgency': self.urgency.value if self.urgency else None,
            'total_cost': self.total_cost,
            'is_urgent': self.is_urgent,
            'is_special_large': self.is_special_large,
            'needs_executive_approval': self.needs_executive_approval,
            'can_be_purchased': self.can_be_purchased,
            'is_pending_approval': self.is_pending_approval,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'shipped_at': self.shipped_at.isoformat() if self.shipped_at else None,
            'arrived_at': self.arrived_at.isoformat() if self.arrived_at else None,
            'price': float(self.price) if self.price else 0,
            'shipping_cost': float(self.shipping_cost) if self.shipping_cost else 0,
        })
        return data
    
    @classmethod
    def get_by_user(cls, user_id: int, include_deleted: bool = False):
        """Get purchases by user"""
        query = cls.query.filter_by(user_id=user_id)
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
        return query.order_by(cls.created_at.desc())
    
    @classmethod
    def get_pending_approval(cls, role: str = None):
        """Get purchases pending approval"""
        query = cls.query.filter_by(is_deleted=False)
        
        if role == 'sublead':
            query = query.filter_by(approval_status=ApprovalStatus.PENDING_SUBLEAD)
        elif role == 'executive':
            query = query.filter_by(approval_status=ApprovalStatus.PENDING_EXECUTIVE)
        else:
            query = query.filter(cls.approval_status.in_([
                ApprovalStatus.PENDING_SUBLEAD,
                ApprovalStatus.PENDING_EXECUTIVE
            ]))
        
        return query.order_by(cls.created_at.desc())
    
    @classmethod
    def get_by_status(cls, status: PurchaseStatus, include_deleted: bool = False):
        """Get purchases by status"""
        query = cls.query.filter_by(status=status)
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
        return query.order_by(cls.created_at.desc())
