from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin_user
from app.crud import dashboard as dashboard_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardOut

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


@router.get("/dashboard", response_model=DashboardOut)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    return dashboard_crud.get_dashboard_stats(db)
