import os

from fastapi import BackgroundTasks, Depends, Header, HTTPException, status
from fastapi.routing import APIRouter
from pydantic import BaseModel

from routes.dependencies import current_user, ensure_admin_user
from services.operations.deployment import DeploymentService


WWW_DEPLOY_ROUTER = APIRouter(prefix="/deploy/www", tags=["www-deployment"])


class NoticeDeployRequest(BaseModel):
    folder: str
    artifact_url: str


class RetryDeployRequest(BaseModel):
    id: str


def _check_deploy_token(deploy_token: str) -> None:
    provided = deploy_token.strip()
    expected = os.environ.get("DEPLOY_NOTICE_TOKEN", "").strip()
    if not expected or provided != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid deployment token.",
        )


def _model_to_dict(model: BaseModel) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


@WWW_DEPLOY_ROUTER.post("/notice")
async def api_notice_www_deployment(
    request: NoticeDeployRequest,
    background_tasks: BackgroundTasks,
    x_deploy_token: str = Header("", alias="X-Deploy-Token"),
):
    _check_deploy_token(x_deploy_token)
    record = DeploymentService.create_record(_model_to_dict(request))
    background_tasks.add_task(DeploymentService.run_deploy, record["id"])
    return {"data": {"id": record["id"], "status": record["status"]}}


@WWW_DEPLOY_ROUTER.get("/all")
async def api_get_www_deployments(user: dict = Depends(current_user)):
    ensure_admin_user(
        user,
        login_detail="You must be logged in to access www deployments.",
        forbidden_detail="You do not have permission to access www deployments.",
    )
    return {"data": DeploymentService.list_records()}


@WWW_DEPLOY_ROUTER.post("/retry")
async def api_retry_www_deployment(
    request: RetryDeployRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(current_user),
):
    ensure_admin_user(
        user,
        login_detail="You must be logged in to retry www deployments.",
        forbidden_detail="You do not have permission to retry www deployments.",
    )
    record = DeploymentService.retry_record(request.id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment record not found.",
        )
    background_tasks.add_task(DeploymentService.run_deploy, record["id"])
    return {"data": record}
