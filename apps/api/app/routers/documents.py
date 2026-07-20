from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from app.database import get_db
from app.dependencies.auth import get_current_company_id, get_current_user
from app.documentation.document_service import DocumentService
from app.models.user import User, UserRole
from app.schemas.document import DocumentGenerateRequest, DocumentResponse, DocumentUpdate

router = APIRouter(prefix="/documents", tags=["documents"])

def require_document_editor(user: User) -> None:
    if user.role == UserRole.VIEWER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Document edit permissions required")

@router.post("/generate/{meeting_id}", response_model=DocumentResponse)
def generate(meeting_id: UUID, body: DocumentGenerateRequest, db=Depends(get_db), company_id: UUID = Depends(get_current_company_id), user: User = Depends(get_current_user)):
    require_document_editor(user)
    return DocumentService(db).generate(meeting_id, company_id, user.id, body.document_type)
@router.get("/{project_id}", response_model=list[DocumentResponse])
def list_documents(project_id: UUID, db=Depends(get_db), company_id: UUID = Depends(get_current_company_id)):
    return DocumentService(db).list_project(project_id, company_id)

detail_router = APIRouter(prefix="/document", tags=["documents"])
@detail_router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: UUID, db=Depends(get_db), company_id: UUID = Depends(get_current_company_id)): return DocumentService(db).get(document_id, company_id)
@detail_router.patch("/{document_id}", response_model=DocumentResponse)
def update_document(document_id: UUID, body: DocumentUpdate, db=Depends(get_db), company_id: UUID = Depends(get_current_company_id), user: User = Depends(get_current_user)):
    require_document_editor(user)
    return DocumentService(db).update(document_id, company_id, body.model_dump(exclude_unset=True))
@detail_router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: UUID, db=Depends(get_db), company_id: UUID = Depends(get_current_company_id), user: User = Depends(get_current_user)):
    require_document_editor(user); DocumentService(db).delete(document_id, company_id); return Response(status_code=204)
@detail_router.get("/{document_id}/export/{format_name}")
def export_document(document_id: UUID, format_name: str, db=Depends(get_db), company_id: UUID = Depends(get_current_company_id)):
    try: data, media_type, suffix = DocumentService(db).export(document_id, company_id, format_name)
    except ValueError: return Response(status_code=422, content="Unsupported export format")
    return StreamingResponse(iter([data]), media_type=media_type, headers={"Content-Disposition": f'attachment; filename="document-{document_id}.{suffix}"'})
