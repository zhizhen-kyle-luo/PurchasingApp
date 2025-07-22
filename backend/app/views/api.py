"""
API routes for purchases and data management
"""
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user

from ..services import PurchaseService, FileService
from ..models import Purchase

api_bp = Blueprint('api', __name__)
purchase_service = PurchaseService()
file_service = FileService()


@api_bp.route('/purchases', methods=['GET'])
@login_required
def get_purchases():
    """Get purchases based on user role and filters"""
    # Get query parameters
    status = request.args.get('status')
    approval_status = request.args.get('approval_status')
    subteam = request.args.get('subteam')
    search = request.args.get('search')
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    filters = {
        'status': status,
        'approval_status': approval_status,
        'subteam': subteam,
        'search': search,
        'include_deleted': include_deleted
    }
    
    try:
        purchases = purchase_service.get_purchases_for_user(current_user, filters)
        
        # Pagination
        total = len(purchases)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_purchases = purchases[start:end]
        
        return jsonify({
            'success': True,
            'purchases': [purchase.to_dict() for purchase in paginated_purchases],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'Failed to get purchases: {str(e)}')
        return jsonify({'success': False, 'message': 'Failed to retrieve purchases'}), 500


@api_bp.route('/purchases', methods=['POST'])
@login_required
def create_purchase():
    """Create a new purchase order"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    result = purchase_service.create_purchase(current_user, data)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': result['message'],
            'purchase': result['purchase'].to_dict()
        }), 201
    else:
        return jsonify({'success': False, 'message': result['message']}), 400


@api_bp.route('/purchases/<int:purchase_id>', methods=['GET'])
@login_required
def get_purchase(purchase_id):
    """Get a specific purchase"""
    purchase = Purchase.query.get(purchase_id)
    
    if not purchase:
        return jsonify({'success': False, 'message': 'Purchase not found'}), 404
    
    # Check permissions
    if current_user.is_requester() and purchase.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    return jsonify({
        'success': True,
        'purchase': purchase.to_dict()
    })


@api_bp.route('/purchases/<int:purchase_id>/approve', methods=['POST'])
@login_required
def approve_purchase(purchase_id):
    """Approve a purchase order"""
    data = request.get_json() or {}
    reason = data.get('reason', '')
    
    result = purchase_service.approve_purchase(purchase_id, current_user, reason)
    
    if result['success']:
        return jsonify({'success': True, 'message': result['message']})
    else:
        return jsonify({'success': False, 'message': result['message']}), 400


@api_bp.route('/purchases/<int:purchase_id>/reject', methods=['POST'])
@login_required
def reject_purchase(purchase_id):
    """Reject a purchase order"""
    data = request.get_json() or {}
    reason = data.get('reason', '')
    
    result = purchase_service.reject_purchase(purchase_id, current_user, reason)
    
    if result['success']:
        return jsonify({'success': True, 'message': result['message']})
    else:
        return jsonify({'success': False, 'message': result['message']}), 400


@api_bp.route('/purchases/<int:purchase_id>/status', methods=['PUT'])
@login_required
def update_purchase_status(purchase_id):
    """Update purchase status"""
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({'success': False, 'message': 'Status is required'}), 400
    
    new_status = data['status']
    photo_filename = data.get('photo_filename')
    
    result = purchase_service.update_purchase_status(
        purchase_id, 
        new_status, 
        current_user,
        photo_filename=photo_filename
    )
    
    if result['success']:
        return jsonify({'success': True, 'message': result['message']})
    else:
        return jsonify({'success': False, 'message': result['message']}), 400


@api_bp.route('/purchases/<int:purchase_id>', methods=['DELETE'])
@login_required
def delete_purchase(purchase_id):
    """Soft delete a purchase"""
    result = purchase_service.delete_purchase(purchase_id, current_user)
    
    if result['success']:
        return jsonify({'success': True, 'message': result['message']})
    else:
        return jsonify({'success': False, 'message': result['message']}), 400


@api_bp.route('/purchases/<int:purchase_id>/restore', methods=['POST'])
@login_required
def restore_purchase(purchase_id):
    """Restore a soft deleted purchase"""
    result = purchase_service.restore_purchase(purchase_id, current_user)
    
    if result['success']:
        return jsonify({'success': True, 'message': result['message']})
    else:
        return jsonify({'success': False, 'message': result['message']}), 400


@api_bp.route('/statistics', methods=['GET'])
@login_required
def get_statistics():
    """Get purchase statistics"""
    try:
        stats = purchase_service.get_purchase_statistics(current_user)
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        current_app.logger.error(f'Failed to get statistics: {str(e)}')
        return jsonify({'success': False, 'message': 'Failed to retrieve statistics'}), 500


@api_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Upload a file"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    subfolder = request.form.get('subfolder', 'arrival_photos')
    
    result = file_service.save_file(file, subfolder)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': result['message'],
            'filename': result['filename']
        })
    else:
        return jsonify({'success': False, 'message': result['message']}), 400
