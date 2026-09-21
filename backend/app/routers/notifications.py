"""
routers/notifications.py — Notification API endpoints for in-app alerts and delivery tracking.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.deps import require_verified, require_admin
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.notification import Notification, NotificationType, NotificationStatus, NotificationCategory

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("/my", summary="Get current user's in-app notifications")
def get_my_notifications(
    unread_only: bool = Query(False),
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
):
    q = db.query(Notification)
    if current_user.role == UserRole.student:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            return {"success": True, "data": []}
        q = q.filter((Notification.student_id == student.id) | (Notification.student_id == None))
    elif current_user.role == UserRole.admin:
        # Admins can see broadcast and system alerts
        pass

    if unread_only:
        q = q.filter(Notification.is_read == False)

    notifications = q.order_by(Notification.created_at.desc()).limit(50).all()

    return {
        "success": True,
        "data": [{
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "notification_type": n.notification_type.value,
            "category": n.category.value,
            "status": n.status.value,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "sent_at": n.sent_at.isoformat() if n.sent_at else None,
        } for n in notifications]
    }


@router.patch("/{notification_id}/read", summary="Mark an in-app notification as read")
def mark_as_read(
    notification_id: int,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    if current_user.role == UserRole.student:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student or (notif.student_id is not None and notif.student_id != student.id):
            raise HTTPException(status_code=403, detail="Access denied")

    notif.is_read = True
    notif.status = NotificationStatus.read
    db.commit()
    return {"success": True, "message": "Notification marked as read"}


@router.get("/all", summary="List all system notifications (admin only)")
def list_all_notifications(
    category: Optional[str] = None,
    notification_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 30,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    q = db.query(Notification)
    if category:
        q = q.filter(Notification.category == category)
    if notification_type:
        q = q.filter(Notification.notification_type == notification_type)

    total = q.count()
    notifications = q.order_by(Notification.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "success": True,
        "data": [{
            "id": n.id,
            "student_id": n.student_id,
            "student_name": (n.student.full_name or n.student.enrollment_no) if n.student else "Broadcast / System",
            "title": n.title,
            "message": n.message,
            "notification_type": n.notification_type.value,
            "category": n.category.value,
            "status": n.status.value,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "sent_at": n.sent_at.isoformat() if n.sent_at else None,
        } for n in notifications],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": -(-total // page_size) if total > 0 else 1,
        }
    }
