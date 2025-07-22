"""
Email service for sending notifications
"""
from typing import Optional, Dict, Any
from flask import current_app, render_template, url_for
from flask_mail import Message, Mail
import logging

from ..models import User, Purchase


class EmailService:
    """Service for handling email notifications"""
    
    def __init__(self, mail_instance: Mail = None):
        self.mail = mail_instance
    
    def _send_email(self, subject: str, recipients: list, html_body: str, text_body: str = None) -> bool:
        """Send email with error handling"""
        if not self.mail:
            current_app.logger.error('Mail instance not configured')
            return False
        
        if current_app.config.get('MAIL_SUPPRESS_SEND', False):
            current_app.logger.info(f'Email suppressed: {subject} to {recipients}')
            return True
        
        try:
            msg = Message(
                subject=subject,
                recipients=recipients,
                html=html_body,
                body=text_body or self._html_to_text(html_body)
            )
            
            self.mail.send(msg)
            current_app.logger.info(f'Email sent successfully: {subject} to {recipients}')
            return True
            
        except Exception as e:
            current_app.logger.error(f'Failed to send email: {subject} to {recipients}. Error: {str(e)}')
            return False
    
    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text (basic implementation)"""
        # This is a basic implementation. For production, consider using libraries like BeautifulSoup
        import re
        text = re.sub('<[^<]+?>', '', html)
        return text.strip()
    
    def send_password_reset_email(self, user: User, token: str) -> bool:
        """Send password reset email"""
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        
        html_body = render_template(
            'email/reset_password.html',
            user=user,
            reset_url=reset_url
        )
        
        return self._send_email(
            subject='Password Reset - MIT Motorsports Purchasing',
            recipients=[user.email],
            html_body=html_body
        )
    
    def send_approval_notification(self, purchase: Purchase, approver_email: str, approval_type: str = 'sublead') -> bool:
        """Send approval notification email"""
        if not approver_email:
            current_app.logger.error('No approver email provided')
            return False
        
        subject = f'Purchase Order Needs {approval_type.title()} Approval - MIT Motorsports'
        
        html_body = render_template(
            'email/approval_notification.html',
            purchase=purchase,
            approval_type=approval_type,
            dashboard_url=url_for('main.dashboard', _external=True)
        )
        
        return self._send_email(
            subject=subject,
            recipients=[approver_email],
            html_body=html_body
        )
    
    def send_approval_status_notification(self, purchase: Purchase, status: str, reason: str = None) -> bool:
        """Send approval status notification to requester"""
        if status == 'approved':
            subject = f'Purchase Order Approved - {purchase.item_name}'
            template = 'email/approval_approved.html'
        else:
            subject = f'Purchase Order Rejected - {purchase.item_name}'
            template = 'email/approval_rejected.html'
        
        html_body = render_template(
            template,
            purchase=purchase,
            reason=reason,
            dashboard_url=url_for('main.dashboard', _external=True)
        )
        
        return self._send_email(
            subject=subject,
            recipients=[purchase.requester_email],
            html_body=html_body
        )
    
    def send_status_update_notification(self, purchase: Purchase, old_status: str, new_status: str) -> bool:
        """Send status update notification"""
        subject = f'Order Status Update - {purchase.item_name}'
        
        html_body = render_template(
            'email/status_update.html',
            purchase=purchase,
            old_status=old_status,
            new_status=new_status,
            dashboard_url=url_for('main.dashboard', _external=True)
        )
        
        return self._send_email(
            subject=subject,
            recipients=[purchase.requester_email],
            html_body=html_body
        )
    
    def send_arrival_notification(self, purchase: Purchase) -> bool:
        """Send arrival notification"""
        subject = f'Your Order Has Arrived - {purchase.item_name}'
        
        html_body = render_template(
            'email/arrival_notification.html',
            purchase=purchase,
            dashboard_url=url_for('main.dashboard', _external=True)
        )
        
        return self._send_email(
            subject=subject,
            recipients=[purchase.requester_email],
            html_body=html_body
        )
    
    def send_bulk_notification(self, subject: str, recipients: list, template: str, **template_vars) -> Dict[str, Any]:
        """Send bulk notification to multiple recipients"""
        result = {'success': 0, 'failed': 0, 'errors': []}
        
        for recipient in recipients:
            try:
                html_body = render_template(template, recipient=recipient, **template_vars)
                
                if self._send_email(subject, [recipient], html_body):
                    result['success'] += 1
                else:
                    result['failed'] += 1
                    result['errors'].append(f'Failed to send to {recipient}')
                    
            except Exception as e:
                result['failed'] += 1
                result['errors'].append(f'Error sending to {recipient}: {str(e)}')
        
        return result
    
    def test_email_configuration(self) -> Dict[str, Any]:
        """Test email configuration"""
        result = {'success': False, 'message': ''}
        
        try:
            # Try to send a test email to the configured sender
            test_subject = 'Email Configuration Test'
            test_body = '<p>This is a test email to verify email configuration.</p>'
            
            if self._send_email(
                subject=test_subject,
                recipients=[current_app.config.get('MAIL_USERNAME')],
                html_body=test_body
            ):
                result['success'] = True
                result['message'] = 'Email configuration is working'
            else:
                result['message'] = 'Failed to send test email'
                
        except Exception as e:
            result['message'] = f'Email configuration error: {str(e)}'
        
        return result
