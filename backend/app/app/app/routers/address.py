from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.address import Address
from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse
# Lưu ý: Thay thế các dependency get_db và get_current_user cho khớp với project thực tế của bạn
# from app.api import deps 

router = APIRouter(prefix="/addresses", tags=["Addresses"])

@router.post("/", response_model=AddressResponse)
def create_address(
    address_in: AddressCreate,
    db: Session = Depends(),          # Thay bằng hàm get_db() của bạn
    current_user = Depends()          # Thay bằng hàm lấy user hiện tại của bạn
):
    if address_in.is_default:
        db.query(Address).filter(Address.user_id == current_user.id).update({Address.is_default: False})
    
    db_address = Address(
        user_id=current_user.id,
        **address_in.dict()
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

@router.get("/", response_model=List[AddressResponse])
def get_my_addresses(
    db: Session = Depends(),
    current_user = Depends()
):
    return db.query(Address).filter(Address.user_id == current_user.id).all()

@router.put("/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: int,
    address_in: AddressUpdate,
    db: Session = Depends(),
    current_user = Depends()
):
    address = db.query(Address).filter(Address.id == address_id, Address.user_id == current_user.id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Không tìm thấy địa chỉ")

    update_data = address_in.dict(exclude_unset=True)
    if update_data.get("is_default") is True:
        db.query(Address).filter(Address.user_id == current_user.id).update({Address.is_default: False})

    for field, value in update_data.items():
        setattr(address, field, value)

    db.commit()
    db.refresh(address)
    return address

@router.delete("/{address_id}")
def delete_address(
    address_id: int,
    db: Session = Depends(),
    current_user = Depends()
):
    address = db.query(Address).filter(Address.id == address_id, Address.user_id == current_user.id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Không tìm thấy địa chỉ")
    
    db.delete(address)
    db.commit()
    return {"message": "Đã xoá địa chỉ thành công"}

@router.patch("/{address_id}/default", response_model=AddressResponse)
def set_default_address(
    address_id: int,
    db: Session = Depends(),
    current_user = Depends()
):
    address = db.query(Address).filter(Address.id == address_id, Address.user_id == current_user.id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Không tìm thấy địa chỉ")

    db.query(Address).filter(Address.user_id == current_user.id).update({Address.is_default: False})
    address.is_default = True
    db.commit()
    db.refresh(address)
    return address