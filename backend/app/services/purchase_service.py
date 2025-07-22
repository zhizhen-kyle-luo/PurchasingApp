"""
Purchase management service
"""
from typing import Optional, Dict, Any, List
from flask import current_app
from sqlalchemy import or_, and_

from ..models import Purchase, User, PurchaseStatus, ApprovalStatus, UrgencyLevel
from ..models.base import db
from .email_service import EmailService


class PurchaseService:
    """Service for handling purchase operations"""
    
    def __init__(self, email_service: EmailService = None):
        self.email_service = email_service or EmailService()
    
    def create_purchase(self, user: User, purchase_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new purchase order"""
        result = {'success': False, 'message': '', 'purchase': None}
        
        try:
            # Validate required fields
            required_fields = ['item_name', 'vendor_name', 'price', 'subteam', 'requester_name', 'requester_email']
            for field in required_fields:
                if not purchase_data.get(field):
                    result['message'] = f'Missing required field: {field}'
                    return result
            
            # Create purchase object
            purchase = Purchase(
                item_name=purchase_data['item_name'],
                vendor_name=purchase_data['vendor_name'],
                item_link=purchase_data.get('item_link', ''),
                price=float(purchase_data['price']),
                shipping_cost=float(purchase_data.get('shipping_cost', 0)),
                quantity=int(purchase_data.get('quantity', 1)),
                subteam=purchase_data['subteam'],
                subproject=purchase_data.get('subproject', ''),
                purpose=purchase_data.get('purpose', ''),
                notes=purchase_data.get('notes', ''),
                requester_name=purchase_data['requester_name'],
                requester_email=purchase_data['requester_email'],
                urgency=UrgencyLevel(purchase_data.get('urgency', 'Neither')),
                user_id=user.id
            )
            
            db.session.add(purchase)
            db.session.commit()
            
            # Send approval notification
            self._send_approval_notification(purchase)
            
            result['success'] = True
            result['message'] = 'Purchase order created successfully'
            result['purchase'] = purchase
            
            current_app.logger.info(f'Purchase created: {purchase.id} by user {user.email}')
            
        except Exception as e:
            db.session.rollback()
            result['message'] = f'Failed to create purchase: {str(e)}'
            current_app.logger.error(f'Purchase creation failed: {str(e)}')
        
        return result
    
    def get_purchases_for_user(self, user: User, filters: Dict[str, Any] = None) -> List[Purchase]:
        """Get purchases based on user role and filters"""
        query = Purchase.query
        
        # Apply role-based filtering
        if user.is_requester():
            query = query.filter_by(user_id=user.id)
        elif user.is_sublead():
            # Subleads can see their team's orders (this could be enhanced with team mapping)
            query = query.filter(
                or_(
                    Purchase.user_id == user.id,
                    Purchase.approval_status == ApprovalStatus.PENDING_SUBLEAD
                )
            )
        # Executives and business users can see all orders
        
        # Apply filters
        if filters:
            if filters.get('status'):
                query = query.filter_by(status=PurchaseStatus(filters['status']))
            
            if filters.get('approval_status'):
                query = query.filter_by(approval_status=ApprovalStatus(filters['approval_status']))
            
            if filters.get('subteam'):
                query = query.filter_by(subteam=filters['subteam'])
            
            if filters.get('include_deleted') is False:
                query = query.filter_by(is_deleted=False)
            
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        Purchase.item_name.ilike(search_term),
                        Purchase.vendor_name.ilike(search_term),
                        Purchase.requester_name.ilike(search_term)
                    )
                )
        
        return query.order_by(Purchase.created_at.desc()).all()
    
    def approve_purchase(self, purchase_id: int, approver: User, reason: str = None) -> Dict[str, Any]:
        """Approve a purchase order"""
        result = {'success': False, 'message': ''}
        
        purchase = Purchase.query.get(purchase_id)
        if not purchase:
            result['message'] = 'Purchase not found'
            return result
        
        try:
            if approver.is_sublead() and purchase.approval_status == ApprovalStatus.PENDING_SUBLEAD:
                purchase.approve_by_sublead(approver.email)
                
                # Send notification to requester
                self.email_service.send_approval_status_notification(purchase, 'approved')
                
                # If needs executive approval, send notification to executive
                if purchase.approval_status == ApprovalStatus.PENDING_EXECUTIVE:
                    self._send_executive_approval_notification(purchase)
                
            elif approver.is_executive() and purchase.approval_status == ApprovalStatus.PENDING_EXECUTIVE:
                purchase.approve_by_executive(approver.email)
                
                # Send notification to requester
                self.email_service.send_approval_status_notification(purchase, 'approved')
                
            else:
                result['message'] = 'Not authorized to approve this purchase'
                return result
            
            result['success'] = True
            result['message'] = 'Purchase approved successfully'
            
            current_app.logger.info(f'Purchase {purchase_id} approved by {approver.email}')
            
        except Exception as e:
            db.session.rollback()
            result['message'] = f'Failed to approve purchase: {str(e)}'
            current_app.logger.error(f'Purchase approval failed: {str(e)}')
        
        return result
    
    def reject_purchase(self, purchase_id: int, rejector: User, reason: str = None) -> Dict[str, Any]:
        """Reject a purchase order"""
        result = {'success': False, 'message': ''}
        
        purchase = Purchase.query.get(purchase_id)
        if not purchase:
            result['message'] = 'Purchase not found'
            return result
        
        if not rejector.can_approve_orders():
            result['message'] = 'Not authorized to reject purchases'
            return result
        
        try:
            purchase.reject(reason)
            
            # Send notification to requester
            self.email_service.send_approval_status_notification(purchase, 'rejected', reason)
            
            result['success'] = True
            result['message'] = 'Purchase rejected successfully'
            
            current_app.logger.info(f'Purchase {purchase_id} rejected by {rejector.email}')
            
        except Exception as e:
            db.session.rollback()
            result['message'] = f'Failed to reject purchase: {str(e)}'
            current_app.logger.error(f'Purchase rejection failed: {str(e)}')
        
        return result
    
    def update_purchase_status(self, purchase_id: int, new_status: str, user: User, **kwargs) -> Dict[str, Any]:
        """Update purchase status"""
        result = {'success': False, 'message': ''}
        
        purchase = Purchase.query.get(purchase_id)
        if not purchase:
            result['message'] = 'Purchase not found'
            return result
        
        if not user.can_manage_orders():
            result['message'] = 'Not authorized to update purchase status'
            return result
        
        try:
            old_status = purchase.status.value
            
            if new_status == 'Purchased':
                purchase.mark_as_purchased()
            elif new_status == 'Shipped':
                purchase.mark_as_shipped()
            elif new_status == 'Arrived':
                photo_filename = kwargs.get('photo_filename')
                purchase.mark_as_arrived(photo_filename)
                
                # Send arrival notification
                self.email_service.send_arrival_notification(purchase)
            else:
                result['message'] = f'Invalid status: {new_status}'
                return result
            
            # Send status update notification
            self.email_service.send_status_update_notification(purchase, old_status, new_status)
            
            result['success'] = True
            result['message'] = f'Purchase status updated to {new_status}'
            
            current_app.logger.info(f'Purchase {purchase_id} status updated to {new_status} by {user.email}')
            
        except ValueError as e:
            result['message'] = str(e)
        except Exception as e:
            db.session.rollback()
            result['message'] = f'Failed to update status: {str(e)}'
            current_app.logger.error(f'Status update failed: {str(e)}')
        
        return result
    
    def delete_purchase(self, purchase_id: int, user: User) -> Dict[str, Any]:
        """Soft delete a purchase"""
        result = {'success': False, 'message': ''}
        
        purchase = Purchase.query.get(purchase_id)
        if not purchase:
            result['message'] = 'Purchase not found'
            return result
        
        # Check permissions
        if not (purchase.user_id == user.id or user.can_manage_orders()):
            result['message'] = 'Not authorized to delete this purchase'
            return result
        
        try:
            purchase.soft_delete()
            
            result['success'] = True
            result['message'] = 'Purchase deleted successfully'
            
            current_app.logger.info(f'Purchase {purchase_id} deleted by {user.email}')
            
        except Exception as e:
            db.session.rollback()
            result['message'] = f'Failed to delete purchase: {str(e)}'
            current_app.logger.error(f'Purchase deletion failed: {str(e)}')
        
        return result
    
    def restore_purchase(self, purchase_id: int, user: User) -> Dict[str, Any]:
        """Restore a soft deleted purchase"""
        result = {'success': False, 'message': ''}
        
        purchase = Purchase.query.get(purchase_id)
        if not purchase:
            result['message'] = 'Purchase not found'
            return result
        
        if not user.can_manage_orders():
            result['message'] = 'Not authorized to restore purchases'
            return result
        
        try:
            purchase.restore()
            
            result['success'] = True
            result['message'] = 'Purchase restored successfully'
            
            current_app.logger.info(f'Purchase {purchase_id} restored by {user.email}')
            
        except Exception as e:
            db.session.rollback()
            result['message'] = f'Failed to restore purchase: {str(e)}'
            current_app.logger.error(f'Purchase restoration failed: {str(e)}')
        
        return result
    
    def get_purchase_statistics(self, user: User = None) -> Dict[str, Any]:
        """Get purchase statistics"""
        query = Purchase.query.filter_by(is_deleted=False)
        
        if user and user.is_requester():
            query = query.filter_by(user_id=user.id)
        
        total_orders = query.count()
        pending_approval = query.filter(
            Purchase.approval_status.in_([
                ApprovalStatus.PENDING_SUBLEAD,
                ApprovalStatus.PENDING_EXECUTIVE
            ])
        ).count()
        
        approved_orders = query.filter_by(approval_status=ApprovalStatus.FULLY_APPROVED).count()
        purchased_orders = query.filter_by(status=PurchaseStatus.PURCHASED).count()
        shipped_orders = query.filter_by(status=PurchaseStatus.SHIPPED).count()
        arrived_orders = query.filter_by(status=PurchaseStatus.ARRIVED).count()
        
        # Calculate total value
        total_value = db.session.query(
            db.func.sum(Purchase.price + Purchase.shipping_cost)
        ).filter_by(is_deleted=False).scalar() or 0
        
        return {
            'total_orders': total_orders,
            'pending_approval': pending_approval,
            'approved_orders': approved_orders,
            'purchased_orders': purchased_orders,
            'shipped_orders': shipped_orders,
            'arrived_orders': arrived_orders,
            'total_value': float(total_value)
        }
    
    def _send_approval_notification(self, purchase: Purchase) -> None:
        """Send approval notification to appropriate approver"""
        # This is a simplified version - in production, you'd have a proper mapping
        # of subteams to sublead emails
        sublead_emails = {
            'MechE Structures': 'sublead1@mit.edu',
            'Electrical': 'sublead2@mit.edu',
            # Add more mappings
        }
        
        sublead_email = sublead_emails.get(purchase.subteam)
        if sublead_email:
            self.email_service.send_approval_notification(purchase, sublead_email, 'sublead')
    
    def _send_executive_approval_notification(self, purchase: Purchase) -> None:
        """Send executive approval notification"""
        # In production, this would be configurable
        exec_emails = ['exec@mit.edu']  # Could be multiple executives
        
        for exec_email in exec_emails:
            self.email_service.send_approval_notification(purchase, exec_email, 'executive')
