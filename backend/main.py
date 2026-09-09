"""
FastAPI应用入口
"""
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api import api_router


async def init_db():
    """初始化数据库，带重试机制"""
    max_retries = 5
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                # 兼容已有开发数据库：create_all 不会为旧表补充新列
                if settings.DATABASE_URL.startswith("postgresql"):
                    from sqlalchemy import text
                    await conn.execute(text("ALTER TABLE topics ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL"))
                    await conn.execute(text("ALTER TABLE topics ADD COLUMN IF NOT EXISTS is_selected BOOLEAN DEFAULT FALSE"))
                    await conn.execute(text("ALTER TABLE \"references\" ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE"))
                    await conn.execute(text("UPDATE \"references\" r SET user_id = p.user_id FROM projects p WHERE r.project_id = p.id AND r.user_id IS NULL"))
                    await conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS word_count INTEGER NOT NULL DEFAULT 10000"))
                    # 兼容早期数据库表结构，补充当前 ORM/接口使用的字段
                    await conn.execute(text("ALTER TABLE outlines ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE"))
                    await conn.execute(text("ALTER TABLE outlines ADD COLUMN IF NOT EXISTS content JSON"))
                    await conn.execute(text("ALTER TABLE outlines ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1"))
                    await conn.execute(text("UPDATE outlines o SET user_id = p.user_id FROM projects p WHERE o.project_id = p.id AND o.user_id IS NULL"))
                    await conn.execute(text("UPDATE outlines SET content = structure WHERE content IS NULL AND structure IS NOT NULL"))
                    await conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE"))
                    await conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS type VARCHAR(50)"))
                    await conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'DRAFT'"))
                    await conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS word_count INTEGER NOT NULL DEFAULT 0"))
                    await conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS content TEXT"))
                    await conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1"))
                    await conn.execute(text("UPDATE documents d SET user_id = p.user_id FROM projects p WHERE d.project_id = p.id AND d.user_id IS NULL"))
                    await conn.execute(text("UPDATE documents SET type = doc_type WHERE type IS NULL AND doc_type IS NOT NULL"))
                    await conn.execute(text("UPDATE documents SET content = structured_content::text WHERE content IS NULL AND structured_content IS NOT NULL"))
            print("Database connected successfully, tables created")
            return
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"Waiting {retry_delay} seconds before retry...")
                await asyncio.sleep(retry_delay)
            else:
                print(f"Database connection failed after max retries: {e}")
                raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时：创建数据库表
    await init_db()

    yield

    # 关闭时：清理资源
    await engine.dispose()


# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI论文写作系统API - AI provider configuration enabled",
    version="1.1.0",
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "ArticleAI API",
        "version": "1.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True,
    )
