from sqlalchemy.orm import Session
from app.models.company import Company
from app.models.workspace import Workspace
from app.models.user import User


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create_company(self, name: str, industry: str | None = None, website: str | None = None, logo: str | None = None) -> Company:
        company = Company(name=name, industry=industry, website=website, logo=logo, subscription_plan="basic")
        self.db.add(company)
        self.db.flush()
        return company

    def create_workspace(self, company_id, workspace_name: str) -> Workspace:
        workspace = Workspace(company_id=company_id, workspace_name=workspace_name)
        self.db.add(workspace)
        self.db.flush()
        return workspace

    def create_user(self, *, company_id, workspace_id, first_name, last_name, email, password_hash, phone, role, status) -> User:
        user = User(
            company_id=company_id,
            workspace_id=workspace_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            phone=phone,
            role=role,
            status=status,
        )
        self.db.add(user)
        self.db.flush()
        return user

    def update_user(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user

    def commit(self) -> None:
        self.db.commit()
