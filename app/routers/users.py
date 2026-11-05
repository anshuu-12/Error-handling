from fastapi import APIRouter, HTTPException, status, Path
from typing import List, Dict
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

fake_users_db: Dict[int, dict] = {}
user_id_counter = 1

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    global user_id_counter
    
    for existing_user in fake_users_db.values():
        if existing_user["email"].lower() == user.email.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A user with email '{user.email}' already exists"
            )

    new_user = user.model_dump()
    new_user["id"] = user_id_counter
    fake_users_db[user_id_counter] = new_user
    user_id_counter += 1
    return new_user

@router.get("/", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def get_users():
    return list(fake_users_db.values())

@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(user_id: int = Path(..., gt=0, description="User ID must be a positive integer")):
    user = fake_users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user

@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user(
    user_update: UserUpdate,
    user_id: int = Path(..., gt=0, description="User ID must be a positive integer")
):
    user = fake_users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    update_data = user_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    user.update(update_data)
    fake_users_db[user_id] = user
    return user

@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: int = Path(..., gt=0, description="User ID must be a positive integer")):
    if user_id not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    del fake_users_db[user_id]
    return {"status": "success", "message": f"User {user_id} deleted successfully"}