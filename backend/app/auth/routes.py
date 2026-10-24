
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.auth.dependencies import CurrentUser
from backend.app.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from backend.app.db.dependencies import get_db
from backend.app.models.database import AuditLog, User
from backend.app.schemas.auth import (
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def write_audit(
    db: Session,
    action: str,
    outcome: str,
    user_id: int | None = None,
) -> None:
    db.add(
        AuditLog(
            actor_user_id=user_id,
            action=action,
            resource_type="user",
            resource_id=str(user_id) if user_id is not None else None,
            outcome=outcome,
        )
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
):
    existing_user = db.scalar(
        select(User).where(User.email == data.email)
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        role="viewer",
        is_active=True,
    )
    db.add(user)

    try:
        db.flush()
        write_audit(db, "USER_REGISTERED", "success", user.id)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    return user


@router.post("/login", response_model=TokenResponse)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    email = form.username.strip().lower()
    user = db.scalar(select(User).where(User.email == email))

    password_hash_to_check = (
        user.password_hash
        if user is not None
        else hash_password("DummyPasswordForTimingOnly123!")
    )
    password_valid = verify_password(
        form.password,
        password_hash_to_check,
    )

    if user is None or not password_valid or not user.is_active:
        write_audit(db, "LOGIN", "denied")
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    write_audit(db, "LOGIN", "success", user.id)
    db.commit()

    token = create_access_token(user.id, user.role)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: CurrentUser):
    return current_user
