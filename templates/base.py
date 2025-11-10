
# Dockerfile 模板
DOCKERFILE_TEMPLATE = """FROM python:3.12.7 AS builds
LABEL authors="unicorn"

WORKDIR /install
COPY requirements.txt requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade setuptools \
    &&  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && mkdir -p /install/lib/python3.12/site-packages \
    && cp -rp /usr/local/lib/python3.12/site-packages /install/lib/python3.12

FROM python:3.12.7
COPY --from=builds /install/lib /usr/local/lib

ARG USER_ID=5000
ARG GID=5000
ARG LOG_DIR=src/app/logs
ARG PORT=8000

WORKDIR /newszjc
COPY . /newszjc
COPY sources.list /etc/apt

#RUN set -xe \
#    && groupadd --gid $GID myuser \
#    && useradd -M -s /user/sbin/nologin -u $USER_ID -g $GID myuser \
#    && echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free" > /etc/apt/sources.list \
#    && echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main contrib non-free" >> /etc/apt/sources.list \
#    && echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list \
#    && apt-get update \
#    && apt-get install -y unixodbc unixodbc-dev \
#    && rm -rf /var/lib/apt/lists/* \
#    && touch $LOG_DIR/app.log \
#    && chown $USER_ID:$GID -R .

RUN rm -rf /etc/apt/sources.list.d/debian.sources

RUN --mount=type=cache,target=/var/cache/apt  \
    apt-get update  \
    && apt-get install -y unixodbc unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

RUN tar -zxvf sqla17developerlinux.tar.gz  \
    && bash sqlany17/setup -silent -I_accept_the_license_agreement -type "Developer Edition"

ENV SQLANY17=/opt/sqlanywhere17
ENV PATH=$SQLANY17/bin64:$SQLANY17/bin32:$PATH
ENV LD_LIBRARY_PATH=$SQLANY17/lib64:$SQLANY17/lib32:$LD_LIBRARY_PATH

RUN mv odbcinst.ini /etc/odbcinst.ini
RUN rm -rf sqlany17  \
    && rm -f sqla17developerlinux.tar.gz

EXPOSE $PORT
#USER myuser
CMD ["python", "main.py"]
"""

# requirements.txt 模板
REQUIREMENTS_TEMPLATE = """aerich~=0.6.0
redis~=5.2
cryptography~=43.0.0
fastapi[all]~=0.112.0
paramiko~=3.5.0
pycryptodome~=3.10.0
pyjwt~=2.9.0
pyodbc~=5.2.0
PyYAML~=6.0.0
tortoise-orm[asyncpg]~=0.19.0
"""

# sources.list 模板
SOURCES_LIST_TEMPLATE = """deb https://mirrors.aliyun.com/debian/ bullseye main non-free contrib
deb-src https://mirrors.aliyun.com/debian/ bullseye main non-free contrib
deb https://mirrors.aliyun.com/debian-security/ bullseye-security main
deb-src https://mirrors.aliyun.com/debian-security/ bullseye-security main
deb https://mirrors.aliyun.com/debian/ bullseye-updates main non-free contrib
deb-src https://mirrors.aliyun.com/debian/ bullseye-updates main non-free contrib
deb https://mirrors.aliyun.com/debian/ bullseye-backports main non-free contrib
deb-src https://mirrors.aliyun.com/debian/ bullseye-backports main non-free contrib
"""

# README.md 模板
README_TEMPLATE = """# {project_name}

## Quick Setup

- Clone with HTTPS [Your Git Repository](http://your-git-repository-yrl.com)

## Environment Setup

1. Create Virtual Environment and Activate

  ```bash
  $ python3 -m venv fastapi_env
  $ source ./fastapi_env/bin/activate
  ```

2. Install Dependencies

   ```bash
   (fastapi_env) $ pip install -r requirements.txt
   ```

3. YAML Configuration
   ```YAML
   app:
     host: 0.0.0.0
     port: 8000
     title: 服务名称
     description: 服务描述
   ```

4. Start Service

   ```bash
   (fastapi_env) $ python src/main.py
   ```

"""

# main.py 模板
MAIN_PY_TEMPLATE = """from contextlib import asynccontextmanager
from urllib.parse import quote

from fastapi import FastAPI, Query
from fastapi.exceptions import (
    HTTPException,
    RequestValidationError,
)
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.app.api.user_module.views import user_router
from src.app.core.config import (
    do_stuff,
    init_db,
    settings,
)
from src.app.utils.middleware.jwt_middleware import JWTMiddleware
from src.app.utils.middleware.signature_middleware import SignatureMiddleware


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    # 在应用启动前初始化数据库连接
    await init_db()
    yield
    # 在应用关闭时关闭数据库连接
    await do_stuff()

app = FastAPI(**settings.FastAPI_SETTINGS, lifespan=lifespan)

# 注册中间件
app.add_middleware(
    CORSMiddleware,
    **settings.CORS
)
app.add_middleware(
    SignatureMiddleware,
    paths_to_verify=settings.PATHS_TO_VERIFY,
)
app.add_middleware(
    JWTMiddleware,
    exclude_paths=settings.TOKEN_EXCLUDE_PATHS
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    err_msg = [f'未传参数: {{error["loc"][-1]}}' if error["type"] == "missing" else error["msg"] for error in errors]

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=err_msg,
        headers={{'WWW-Authenticate': 'Bearer'}},
    )

app.include_router(user_router, prefix='/user')

if name == 'main':
    import uvicorn
    uvicorn.run(
        app='main:app',
        host=settings.host,
        port=settings.port,
        reload=True
    )

"""
