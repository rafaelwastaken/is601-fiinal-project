from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models as _models
from app.crud.calculation import (
    create_calculation,
    delete_calculation,
    get_calculation,
    list_calculations,
    update_calculation,
)
from app.crud.user import build_unique_username, create_user, get_user_by_email, get_user_by_username
from app.db.session import Base, engine, get_db
from app.schemas.calculation import CalculationCreate, CalculationRead, CalculationUpdate
from app.schemas.user import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserRead,
)
from app.security import create_access_token, verify_password


Base.metadata.create_all(bind=engine)

app = FastAPI(title="IS601 Module 12 API")

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/register.html", include_in_schema=False)
def register_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "register.html")


@app.get("/login.html", include_in_schema=False)
def login_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "login.html")


@app.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already exists")

    username = build_unique_username(db, payload.email)

    try:
        create_user(
            db,
            UserCreate(username=username, email=payload.email, password=payload.password),
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="user already exists")

    token = create_access_token(payload.email)
    return TokenResponse(access_token=token)


@app.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = get_user_by_email(db, payload.email)

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    token = create_access_token(user.email)
    return TokenResponse(access_token=token)


@app.post("/users/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    if get_user_by_username(db, payload.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="username already exists")

    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already exists")

    try:
        user = create_user(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="user already exists")

    return UserRead.model_validate(user)


@app.post("/users/login", response_model=LoginResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)) -> LoginResponse:
    user = get_user_by_username(db, payload.username)

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    return LoginResponse(message="login successful")


@app.get("/calculations", response_model=list[CalculationRead])
def browse_calculations(db: Session = Depends(get_db)) -> list[CalculationRead]:
    calculations = list_calculations(db)
    return [CalculationRead.model_validate(calculation) for calculation in calculations]


@app.post("/calculations", response_model=CalculationRead, status_code=status.HTTP_201_CREATED)
def add_calculation(payload: CalculationCreate, db: Session = Depends(get_db)) -> CalculationRead:
    calculation = create_calculation(db, payload)
    return CalculationRead.model_validate(calculation)


@app.get("/calculations/{calculation_id}", response_model=CalculationRead)
def read_calculation(calculation_id: int, db: Session = Depends(get_db)) -> CalculationRead:
    calculation = get_calculation(db, calculation_id)
    if not calculation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="calculation not found")
    return CalculationRead.model_validate(calculation)


@app.put("/calculations/{calculation_id}", response_model=CalculationRead)
def edit_calculation(
    calculation_id: int,
    payload: CalculationUpdate,
    db: Session = Depends(get_db),
) -> CalculationRead:
    calculation = get_calculation(db, calculation_id)
    if not calculation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="calculation not found")

    updated = update_calculation(db, calculation, payload)
    return CalculationRead.model_validate(updated)


@app.delete("/calculations/{calculation_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_calculation(calculation_id: int, db: Session = Depends(get_db)) -> None:
    calculation = get_calculation(db, calculation_id)
    if not calculation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="calculation not found")

    delete_calculation(db, calculation)
