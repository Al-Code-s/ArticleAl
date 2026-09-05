"""
API路由汇总
"""
from fastapi import APIRouter
from app.api import auth, projects, topics, outlines, references, documents, chat, export

api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(projects.router, prefix="/projects", tags=["项目"])
api_router.include_router(topics.router, prefix="/topics", tags=["选题"])
api_router.include_router(outlines.router, prefix="/outlines", tags=["大纲"])
api_router.include_router(references.router, prefix="/references", tags=["参考文献"])
api_router.include_router(documents.router, prefix="/documents", tags=["文档"])
api_router.include_router(chat.router, prefix="/chat", tags=["聊天"])
api_router.include_router(export.router, prefix="/export", tags=["导出"])

# 健康检查
@api_router.get("/health", tags=["系统"])
async def health():
    """健康检查"""
    return {"status": "healthy"}
