from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import settings
from src.api.routers import auth, chat, report, admin, knowledge

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["Chat"])
app.include_router(report.router, prefix=f"{settings.API_V1_STR}/report", tags=["Report"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}", tags=["Admin"])  # 注意：admin router 自带了 /admin 前缀
app.include_router(knowledge.router, prefix=f"{settings.API_V1_STR}/knowledge", tags=["Knowledge"])

@app.get("/")
async def root():
    return {"message": "Welcome to Healthy RAG API"}

