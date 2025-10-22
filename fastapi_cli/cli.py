import subprocess
import sys
from pathlib import Path

# 镜像映射表
MIRROR_MAP = {
    'default': 'https://pypi.org/simple',
    'tuna': 'https://pypi.tuna.tsinghua.edu.cn/simple',
    'aliyun': 'https://mirrors.aliyun.com/pypi/simple',
    # 待添加
}

# 数据库配置模板
DB_CONFIG_TEMPLATES = {
    'postgres': {
        'config': """
    pg_configs = config.get('pg')
    DATABASES = {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": pg_configs.get('host', '127.0.0.1'),
                "port": pg_configs.get('port', 5432),
                "user": pg_configs.get('user', 'postgres'),
                "password": pg_configs.get('password', 'postgres'),
                "database": pg_configs.get('db', 'postgres'),
            }
        }
    }
        """,
        'yaml_template': """
pg:
  host: 127.0.0.1
  port: 5432
  user: pg_user
  password: pg_password
  db: database_name
        """,
    },
    'mysql': {
        'config': """
    mysql_configs = config.get('mysql')
    MYSQL_DATABASES = {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": mysql_configs.get('host', '127.0.0.1'),
                "port": mysql_configs.get('port', 3306),
                "user": mysql_configs.get('user', 'root'),
                "password": mysql_configs.get('password', ''),
                "database": mysql_configs.get('db', 'test'),
                "charset": "utf8mb4",
            }
        }
    }
        """,
        'yaml_template': """
mysql:
  host: 127.0.0.1
  port: 3306
  user: mysql_user
  password: mysql_password
  db: database_name
        """,
    },
    'redis': {
        'config': """
    redis_settings = config.get('redis')
    REDIS_CONFIG = {
        'db_name': 'default_redis',
        'host': redis_settings.get('host', 'localhost'),
        'port': int(redis_settings.get('port', 6379)),
        'db': int(redis_settings.get('db', 0)),
        'password': redis_settings.get('password', ''),
        'socket_timeout': 180,
        'retry_on_timeout': True,
        'decode_responses': True,
    }
        """,
        'yaml_template': """
redis:
  host: 127.0.0.1
  port: 6379
  db: 0
  password: redis_password
        """,
    },
    'sqlite': {
        'config': """
    sqlite_configs = config.get('sqlite')
    SQLITE_DATABASES = {
        "default": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {
                "file_path": sqlite_configs.get('file_path', 'db.sqlite3'),
            }
        }
    }
        """,
        'yaml_template': """
sqlite:
  file_path: db.sqlite3
        """,
    },
}


class ProjectCreator:
    def __init__(self):
        self.project_structure = {
            'Dockerfile': self.get_dockerfile_template(),
            'README.md': self.get_readme_template(),
            'requirements.txt': self.get_requirements_template(),
            'sources.list': self.get_sources_list_template(),
            'src': {
                'main.py': self.get_main_py_template(),
                'app': {
                    '__init__.py': '',
                    'core': {
                        '__init__.py': '',
                        'config.py': self.get_config_py_template(),
                    },
                    'api': {
                        '__init__.py': '',
                        'user_module': {
                            '__init__.py': '',
                            'views.py': self.get_user_views_py_template(),
                            'models.py': self.get_user_models_py_template(),
                            'data_pydantic.py': self.get_user_data_pydantic_py_template(),
                        }
                    },
                    'utils': {
                        '__init__.py': '',
                        'aes_tools.py': self.get_aes_tools_template(),
                        'authorization_tools.py': self.get_authorization_tools_template(),
                        'db_tools.py': self.get_db_tools_template(),
                        'hash_tools.py': self.get_hash_tools_template(),
                        'rsa_tools.py': self.get_rsa_tools_template(),
                        'signature_tools.py': self.get_signature_tools_template(),
                        'middleware': {
                            '__init__.py': '',
                            'jwt_middleware.py': self.get_jwt_middleware_template(),
                            'signature_middleware.py': self.get_signature_middleware_template(),
                            'timer_middleware.py': self.get_timer_middleware_template(),
                        }
                    },
                    'templates': {
                        'base.html': self.get_base_html_template(),
                        'index.html': self.get_index_html_template(),
                        'common': {
                            'header.html': self.get_header_html_template(),
                            'footer.html': self.get_footer_html_template(),
                        }
                    }
                }
            }
        }

    def get_dockerfile_template(self):
        """Dockerfile 模板"""
        return """FROM python:3.12.7 AS builds
LABEL authors="your_name"

WORKDIR /install
COPY requirements.txt requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \\
    pip install --upgrade setuptools \\
    &&  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple  \\
    && mkdir -p /install/lib/python3.12/site-packages \\
    && cp -rp /usr/local/lib/python3.12/site-packages /install/lib/python3.12

FROM python:3.12.7
COPY --from=builds /install/lib /usr/local/lib

ARG USER_ID=5000
ARG GID=5000
ARG LOG_DIR=src/app/logs
ARG PORT=8000

WORKDIR /worker_dir
COPY . /worker_dir
COPY sources.list /etc/apt

EXPOSE $PORT
CMD ["python", "src/main.py"]
        """

    def get_readme_template(self):
        """README.md 模板"""
        return """# FastAPI Template

## Quick Setup -- If You've Done This Kind of Thing Before

- Clone with HTTPS [Project Git Repository Url](https://exam-domain.com)

## ...or Create A New Repository on the Command Line

```bash
$ echo "# FastAPI Template" >> README.md
$ git init
$ git add README.md
$ git commit -m "add README file"
$ git branch -M main
$ git remote add origin https://exam-domain.com
$ git push -u origin main
```

## ...or Push An Existing Repository from the Command Line

```bash
$ git remote add origin https://exam-domain.com
$ git branch -M main
$ git push -u origin main
```

## Create Dependent Environment 创建依赖环境

1. 创建虚拟环境并激活
   1. Python3 venv 模块
   
      ```bash
      $ python3 -m venv fastapi_env
      $ source ./fastapi_env/bin/activate
      ```
   
      - Conda (Anaconda or Miniconda)
   
         ```bash
         $ conda create -n fastapi_env python=3.10
         $ conda active fastapi_env
         ```
         
2. 安装依赖

   ```bash
   (fastapi_env) $ pip install -r requirements.txt
   ```

3. YAML 文件数据库连接配置

   ```YAML
   app:
     host: 0.0.0.0
     port: 8000
     title: 服务名称
     description: 服务描述
   ```
   
   生产环境文件名: CONFIG_PROD.yml
   测试环境文件名: CONFIG_TEST.yml
   开发环境文件名: CONFIG_DEV.yml

4. 启动服务
   运行 main.py 文件
   ```bash
   (fastapi_env) $ python src/main.py
   ```
   uvicorn 命令
   ```bash
   (fastapi_env) $ uvicorn src/main:app --host=127.0.0.1 --port=8000 --reload
   ```
        """

    def get_requirements_template(self):
        """requirements.txt 模板"""
        return """aerich~=0.6.0
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

    def get_sources_list_template(self):
        """sources.list 模板"""
        return """deb https://mirrors.aliyun.com/debian/ bullseye main non-free contrib
deb-src https://mirrors.aliyun.com/debian/ bullseye main non-free contrib
deb https://mirrors.aliyun.com/debian-security/ bullseye-security main
deb-src https://mirrors.aliyun.com/debian-security/ bullseye-security main
deb https://mirrors.aliyun.com/debian/ bullseye-updates main non-free contrib
deb-src https://mirrors.aliyun.com/debian/ bullseye-updates main non-free contrib
deb https://mirrors.aliyun.com/debian/ bullseye-backports main non-free contrib
deb-src https://mirrors.aliyun.com/debian/ bullseye-backports main non-free contrib
        """

    def get_main_py_template(self):
        """main.py 模板"""
        return """from contextlib import asynccontextmanager
from urllib.parse import quote

from fastapi import FastAPI
from fastapi.exceptions import (
    HTTPException,
    RequestValidationError,
)
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

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
    err_msg = [f'未传参数: {error["loc"][-1]}' if error["type"] == "missing" else error["msg"] for error in errors]

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=err_msg,
        headers={'WWW-Authenticate': 'Bearer'},
    )

app.include_router(user_router, prefix='/user')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app='main:app',
        host=settings.host,
        port=settings.port,
        reload=True
    )

    """

    def get_config_py_template(self):
        """config.py 模板"""
        return """import asyncio
import os
import pathlib

import pytz
import yaml
from starlette.templating import Jinja2Templates
from tortoise import Tortoise

RUN_ENV = os.environ.get('RUN_ENV', 'PROD')
OS_USER = os.environ.get('USER', 'root')
PATH = pathlib.Path(__file__).parent.parent.parent.parent


def load_yaml_config():
    config_file = f'CONFIG_{RUN_ENV}.yml'

    try:
        with open(PATH / config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return config
    except FileNotFoundError:
        raise RuntimeError(f'配置文件 {config_file} 不存在, 请按 README.md 文件中的格式新建配置文件')


class Settings:
    config = load_yaml_config()

    RUN_ENV = RUN_ENV

    app_configs = config.get('app')
    host = app_configs.get('host')
    port = app_configs.get('port')
    FastAPI_SETTINGS = {
        "title": app_configs.get('title'),
        "description": app_configs.get('description'),
        "version": "0.0.1",
    }
    sem = asyncio.Semaphore(30)         # 控制项目中 异步请求其他网址时的并发量
    retry = 30                          # 网络重访次数

    # 数据库配置将根据用户选择动态生成

    CORS = {
        "allow_origins": ['*'],             # 设置允许的 origins 来源
        "allow_credentials": True,
        "allow_methods": ['*'],             # 设置允许跨域的 HTTP 方法
        "allow_headers": ['*'],             # 允许跨域的 headers, 可以用来鉴别来源等作用
    }
    PATHS_TO_VERIFY = {
        '/user/register',
        '/user/activation',
        '/user/authentication_token',
    }
    TOKEN_EXCLUDE_PATHS = {
        '/docs',
        '/openapi.json',
        '/user/register',
        '/user/activation',
        '/user/authentication_token',
        '/favicon.ico',
        '/loading',
    }

    # 程序配置
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_path = os.path.join(BASE_DIR, 'logs')           # 日志目录
    if not os.path.exists(log_path):
        os.mkdir(log_path)

    # 模板配置
    TEMPLATES = Jinja2Templates(directory='src/app/templates')

    BASE_DOMAIN = 'https://exam-domain.com '

    # 签名和 token 加密 Key
    SECRET_KEY = 'EXAMPLE-SECRET-KEY'
    REFRESH_TOKEN_SECRET_KEY = 'REFRESH-TOKEN-SECRET-KEY'
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 15
    REFRESH_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 7
    # RSA 密钥长度
    RSA_KEY_SIZE = 2048

    LOCAL_TIMEZONE = pytz.timezone('PRC')


settings = Settings


async def init_db():
    try:
        await Tortoise.init(config=settings.TORTOISE_ORM)
        await Tortoise.generate_schemas()
    except ConnectionRefusedError as e:
        print(e)


async def do_stuff():
    await Tortoise.close_connections()

    """

    def get_user_views_py_template(self):
        """user_module/views.py 模板"""
        return '''import hashlib
import logging
import time
import traceback
from datetime import datetime, timedelta
from urllib.parse import quote

import jwt
import ujson
from fastapi.routing import APIRouter
from jwt import ExpiredSignatureError
from starlette import status
from starlette.exceptions import HTTPException

from src.app.api.user_module.data_pydantic import (
    BaseUserItem,
    RefreshTokenItem,
    UserActivationItem,
    UserAuthenticationItem,
)
from src.app.api.user_module.models import (
    Users,
    VirtualDatabase,
)
from src.app.core.config import settings
from src.app.utils.aes_tools import AESCrypto
from src.app.utils.authorization_tools import (
    create_authorization_code,
    create_token,
)
from src.app.utils.db_tools import (
    DatabasePool,
)
from src.app.utils.hash_tools import create_hash_summary
from src.app.utils.rsa_tools import (
    YOUR_PRIVATE_KEY,
    YOUR_PUBLIC_KEY,
    decryption_message,
    encryption_message,
)

user_router = APIRouter()
logger = logging.getLogger(__name__)
activation_token_prefix = 'ACTIVATION_TOKEN_'


@user_router.post('/register')
async def user_register(item: BaseUserItem):
    """用户注册"""
    # 检查用户是否已经存在
    user = await Users.filter(phone=item.phone).first()
    if user:
        return {'msg': '已存在'}

    try:
        # 生成用户授权码 auth_code
        auth_code = create_authorization_code()
        # 默认密码 abc123456
        password = create_hash_summary('abc123456')
        # 创建用户
        user = await Users(
            phone=item.phone,
            nick_name=f'用户_{item.phone}',
            auth_code=auth_code,
            password=password,
        )
        await user.save()
        # 基于用户 id 生成激活链接并存 redis
        message = ujson.dumps({'uid': user.id, 'phone': user.phone})
        activation_token = encryption_message(message, YOUR_PUBLIC_KEY)
        pool = DatabasePool()
        redis_client = pool.redis_db_dict[settings.REDIS_CONFIG['db_name']]
        key = f'{activation_token_prefix}{activation_token}'
        await redis_client.set(key, user.phone)
    except Exception as e:
        logger.error(f'注册失败:\n{traceback.format_exc()}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            headers={'WWW-Authenticate': 'Bearer'}
        )

    return {'msg': '注册成功', 'auth_code': auth_code, 'activation_token': activation_token}


@user_router.post('/activation')
async def user_activation(item: UserActivationItem):
    pool = DatabasePool()
    redis_client = pool.redis_db_dict[settings.REDIS_CONFIG['db_name']]
    redis_phone = await redis_client.get(f'{activation_token_prefix}{item.activation_token}')

    if not redis_phone:
        logger.warning(f'无效的激活口令: {item.activation_token}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='无效的激活口令',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    message = decryption_message(item.activation_token, YOUR_PRIVATE_KEY)
    data = ujson.loads(message)

    if not data.get('phone') or 'uid' not in data or redis_phone != data['phone']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='激活口令无效',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    user = await Users.get(id=data.get('uid'))
    if not user or user.is_delete:
        logger.warning(f'用户不存在: {data.get("phone")}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='用户不存在',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        user.is_active = True
        await user.save()

        # 删除 redis 中的 activation_token
        await redis_client.delete(f'{activation_token_prefix}{item.activation_token}')
    except Exception:
        logger.error(f'激活失败:\n{traceback.format_exc()}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='激活失败',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return {'msg': '激活成功'}


@user_router.post('/authentication_token')
async def user_authentication_token(item: UserAuthenticationItem):
    this_time = int(time.time())

    user = await Users.filter(phone=item.phone).first()
    if not user or user.is_delete:
        logger.warning(f'用户不存在: {item.phone}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='用户不存在',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    elif not user.is_active:
        return {'msg': '用户未激活, 请先激活'}

    # 解密 secret_msg
    message = decryption_message(item.secret_msg, YOUR_PRIVATE_KEY)
    data = ujson.loads(message)

    if not data.get('auth_code') or not data.get('timestamp'):
        logger.warning(f'认证信息错误: {item.phone}')
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='认证信息错误',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    elif user.auth_code != data['auth_code']:
        logger.warning(f'错误授权码: {item.phone}')
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='错误授权码',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    elif abs(this_time - data['timestamp']) > 60:
        logger.warning(f'认证信息失效: {item.phone}')
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail='认证信息失效',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        user.last_login = datetime.today()
        access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
        access_token = create_token(
            data={'uid': user.id, 'phone': user.phone},
            secret_key=settings.SECRET_KEY,
            expires_delta=access_token_expires,
        )

        refresh_token_expires = timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_SECONDS)
        refresh_token = create_token(
            data={'uid': user.id, 'phone': user.phone},
            secret_key=settings.REFRESH_TOKEN_SECRET_KEY,
            expires_delta=refresh_token_expires,
        )

        return {'msg': '登录成功', 'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}
    except Exception as e:
        logger.error(f'登录失败:\n{traceback.format_exc()}')
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='登录失败',
            headers={'WWW-Authenticate': 'Bearer'},
        )


@user_router.post('/token/refresh')
async def check_refresh_token_get_new_token(item: RefreshTokenItem):
    try:
        payload = jwt.decode(
            item.refresh_token,
            settings.REFRESH_TOKEN_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True}
        )
        uid: int = payload.get('uid')

        if not uid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='重刷 Token 错误')

        user = await Users.get(id=uid)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='用户不存在')

        access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
        access_token = create_token(
            data={'uid': user.id, 'phone': user.phone},
            secret_key=settings.SECRET_KEY,
            expires_delta=access_token_expires,
        )
        return {'access_token': access_token, 'expires': settings.ACCESS_TOKEN_EXPIRE_SECONDS}
    except ExpiredSignatureError:
        logger.error('重刷 Token 已过期')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='重刷 Token 已过期')
    except Exception as e:
        logger.error(f'重刷 Token 失败:\n{traceback.format_exc()}')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

        '''

    def get_init_subapp_views_py_templdate(self):
        """初始化子应用的 viuews.py 模板"""
        return """import logging

from fastapi.routing import APIRouter

logger = logging.getLogger(__name__)

        """

    def get_user_models_py_template(self):
        """user_module/models.py 模板"""
        return """import time

from tortoise import Model, fields


class Users(Model):
    id = fields.IntField(pk=True)
    phone = fields.CharField(max_length=16, index=True, unique=True, null=False, description='用户手机号')
    auth_code = fields.CharField(max_length=64, null=False, description='用户授权码')
    password = fields.CharField(max_length=64, null=True, description='用户自设密码')
    nick_name = fields.CharField(max_length=32, null=True, description='昵称')
    age = fields.IntField(default=0, description='年龄')
    gender = fields.CharField(max_length=8, default='male', description='性别')
    avatar = fields.CharField(max_length=256, default='', description='头像')
    create_at = fields.DatetimeField(auto_now_add=True, description='创建时间')
    update_at = fields.DatetimeField(auto_now=True, description='更新时间')
    last_login = fields.DatetimeField(null=True, description='最后登录时间')
    is_active = fields.BooleanField(default=False, description='是否激活')
    is_delete = fields.BooleanField(default=False, description='是否已删除')

    async def save(self, *args, **kwargs):
        # 限制年龄在 0~120岁之间
        if self.age < 0 or self.age > 120:
            raise ValueError('年龄必须在 0~120 岁之间')
        await super(Users, self).save(*args, **kwargs)

    class Meta:
        table = 'user'

        """

    def get_init_subapp_modesl_py_templdate(self):
        """初始化子应用的 models.py 模板"""
        return """from tortoise import Model, fields

        """

    def get_user_data_pydantic_py_template(self):
        """user_module/data_pydantic.py 模板"""
        return """from pydantic import BaseModel


class BaseUserItem(BaseModel):
    phone: str


class UserActivationItem(BaseModel):
    activation_token: str


class UserAuthenticationItem(BaseUserItem):
    secret_msg: str


class RefreshTokenItem(BaseModel):
    refresh_token: str

        """

    def get_init_subapp_data_pydantic_py_template(self):
        """初始化子应用的 data_pydantic.py 模板"""
        return """from pydantic import BaseModel

        """

    def get_aes_tools_template(self):
        """aes_tools.py 模板"""
        return """import base64
from urllib.parse import unquote

import ujson
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class AESCrypto:
    def __init__(self, encoding_aes_key):
        self.aes_key = encoding_aes_key.encode()

    def ecb_encrypt(self, content):
        content = pad(bytes(content, 'utf-8'), AES.block_size)

        # AES 对象
        aes_encode = AES.new(self.aes_key, AES.MODE_ECB)

        # 加密
        encrypt_res = aes_encode.encrypt(content)

        return base64.b64encode(encrypt_res).decode().replace('\n', '')

    def ecb_decrypt(self, content):
        content = base64.b64decode(unquote(unquote(content)))

        aes_decode = AES.new(self.aes_key, AES.MODE_ECB)

        decode_res = aes_decode.decrypt(content)

        return unpad(decode_res, AES.block_size)

    def loads_ecb_decrypt(self, content):
        return ujson.loads(self.ecb_decrypt(content))

        """

    def get_authorization_tools_template(self):
        """authorization_tools.py 模板"""
        return '''import random
import secrets
import string
from datetime import datetime, timedelta

import jwt

from src.app.core.config import settings


def create_token(data: dict, secret_key: str, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(tz=settings.LOCAL_TIMEZONE) + expires_delta
    else:
        expire = datetime.now(tz=settings.LOCAL_TIMEZONE) + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)

    to_encode['exp'] = expire
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)

    return encoded_jwt


def create_authorization_code(length: int = 32, max_special_chars: int = 5):
    """用户授权码"""
    special_chars = '!@#$%&*-_+=?;:~'
    num_special_chars = 1 + secrets.randbelow(min(len(special_chars), max_special_chars))
    special_parts = ''.join(random.sample(special_chars, num_special_chars))

    remaining_chars = string.ascii_letters + string.digits
    remaining_parts = ''.join(random.choice(remaining_chars) for _ in range(length - num_special_chars))

    combine = list(remaining_parts + special_parts)
    random.shuffle(combine)

    return ''.join(combine)

        '''

    def get_db_tools_template(self):
        """db_tools.py 模板"""
        return """import asyncio
import logging
import re
import subprocess
import traceback

import pyodbc
from redis import asyncio as aioredis

from src.app.api.user_module.models import Users
from src.app.core.config import settings

logger = logging.getLogger(__name__)


class DatabasePool:

    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'redis_db_dict'):
            self.redis_db_dict = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(DatabasePool, cls).__new__(cls)

        return cls._instance

    async def create_redis_pool(self, redis_config):
        redis_config = redis_config.copy()
        db_name = redis_config.pop('db_name', 'teaching_digital_material')

        # 创建链接池
        if not self.redis_db_dict.get(db_name):
            pool = aioredis.ConnectionPool(**redis_config)
            self.redis_db_dict[db_name] = await aioredis.Redis(connection_pool=pool)

    async def close_redis_pool(self, db_name):
        redis_pool = self.redis_db_dict.get(db_name)
        if redis_pool:
            await redis_pool.close()

    async def close_all_redis_pool(self):
        for db_name, redis_pool in self.redis_db_dict.items():
            await redis_pool.close()

        """

    def get_hash_tools_template(self):
        """hash_tools.py 模板"""
        return """import hashlib


def create_hash_summary(data: str):
    sha256_hash = hashlib.sha256(data.encode('utf-8'))
    return sha256_hash.hexdigest()

        """

    def get_rsa_tools_template(self):
        """rsa_tools.py 模板"""
        return """import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from src.app.core.config import settings

# 数字教材 RSA 私钥和公钥
YOUR_PRIVATE_KEY = (
    'YOUR_PRIVATE_KEY',
)
YOUR_PUBLIC_KEY = (
    'YOUR_PUBLIC_KEY',
)


def create_rsa_private_public_key(key_size: int = 0) -> tuple[str, str]:
    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size or settings.RSA_KEY_SIZE,
        backend=default_backend,
    )

    # 从私钥导出公钥
    public_key = private_key.public_key()

    # 序列化为 PEM 格式
    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pem_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return pem_private_key.decode('utf-8'), pem_public_key.decode('utf-8')


def get_public_key(str_private_key: str) -> str:
    private_key = serialization.load_pem_private_key(
        str_private_key.encode('utf-8'),
        password=None,
    )

    public_key = private_key.public_key()
    pem_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return pem_public_key.decode('utf-8')


def decryption_message(message, str_private_key):
    private_key = serialization.load_pem_private_key(
        str_private_key.encode('utf-8'),
        password=None,
    )

    ciphertext = base64.b64decode(message.encode('utf-8'))
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        )
    )
    return plaintext.decode('utf-8')


def encryption_message(message, str_public_key):
    public_key = serialization.load_pem_public_key(
        str_public_key.encode('utf-8'),
    )

    ciphertext = public_key.encrypt(
        message.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        )
    )

    return base64.b64encode(ciphertext).decode('utf-8')

        """

    def get_signature_tools_template(self):
        """signature_tools.py 模板"""
        return '''import hashlib
import hmac
import time
from typing import Dict

from src.app.core.config import settings
from src.app.utils.aes_tools import AESCrypto


def generate_signature(params: Dict[str, str]) -> str:
    """生成签名"""
    sorted_params = sorted(params.items())
    encoded_params = '&'.join(f'{key}={value}' for key, value in sorted_params)
    return hmac.new(settings.SECRET_KEY.encode(), encoded_params.encode(), hashlib.sha256).hexdigest()


def verify_signature(params: Dict[str, str], signature: str) -> bool:
    """验证签名"""
    generated_signature = generate_signature(params)
    return hmac.compare_digest(generated_signature, signature)

        '''

    def get_jwt_middleware_template(self):
        """jwt_middleware.py 模板"""
        return """import logging

import jwt
from jwt import (
    DecodeError,
    ExpiredSignatureError,
    InvalidSignatureError,
)
from starlette import status
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import (
    JSONResponse,
    Response,
)

from src.app.api.user_module.models import Users
from src.app.core.config import settings

logger = logging.getLogger(__name__)


async def check_jwt_payload(token, verify_exp: bool = True):
    payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": verify_exp}
        )
    uid: int = payload.get('uid')
    if not uid:
        raise Exception('错误身份标识')

    user = await Users.get(id=uid)
    if not user:
        raise Exception('无效身份标识')

    return user, payload.get('port')


class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exclude_paths: set):
        super(JWTMiddleware, self).__init__(app)
        self.exclude_paths = exclude_paths

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        authorization: str = request.headers.get('Authorization', '')
        if not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'msg': '没有身份标识'},
            )

        token = authorization.split(' ')[1]

        try:
            request.state.user, request.state.port = await check_jwt_payload(token, verify_exp=True)
        except ExpiredSignatureError:
            # 有了重刷 Token, 不需要在过期时关闭服务
            # # jwt 过期: 检查服务是否存在, 已存在关闭
            # user, port = await check_jwt_payload(token, verify_exp=False)
            # await close_user_asa_service(user)

            logger.warning(f'URL {request.url.path} 身份已过期')
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'msg': '身份已过期'},
            )
        except InvalidSignatureError:
            logger.warning(f'URL {request.url.path} 错误或无效身份标识')
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'msg': '错误或无效身份标识'},
            )
        except DecodeError:
            logger.warning(f'URL {request.url.path} 无法解码 Token')
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'msg': '无法解码 Token'}
            )
        except Exception as e:
            logger.warning(f'URL {request.url.path} 认证失败: {str(e)}')
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'msg': f'认证失败: {str(e)}'},
            )

        response = await call_next(request)

        return response

        """

    def get_signature_middleware_template(self):
        """signature_middleware.py 模板"""
        return """import logging
from urllib.parse import parse_qs

import ujson
from starlette import status
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import (
    JSONResponse,
    Response,
)

from src.app.utils.signature_tools import verify_signature

logger = logging.getLogger(__name__)


class SignatureMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, paths_to_verify: set):
        super(SignatureMiddleware, self).__init__(app)
        self.paths_to_verify = paths_to_verify

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in self.paths_to_verify:
            query_params = parse_qs(str(request.query_params))
            query_params = {k: ','.join(v) for k, v in query_params.items()}
            body_bytes = await request.body()
            body = ujson.loads(body_bytes)

            async def receive() -> dict:
                return {'type': 'http.request', 'body': body_bytes}

            request._receive = receive

            params = {**query_params, **body}

            signature = request.headers.get('sign', '')
            if not signature:
                logger.warning('缺少必要请求头参数: sign')
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={'msg': '缺少必要请求头参数: sign'},
                )

            if not verify_signature(params, signature):
                logger.warning('请求参数不合法')
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={'msg': '请求参数不合法'},
                )

        response = await call_next(request)

        return response

        """

    def get_timer_middleware_template(self):
        """timer_middleware.py 模板"""
        return """import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class TimerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, active_paths: set):
        super(TimerMiddleware, self).__init__(app)
        self.active_paths = active_paths

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path not in self.active_paths:
            return await call_next(request)

        start_time = time.time()
        response = await call_next(request)
        finish_time = time.time()

        print(f"Page: {request.url.path} spend time {finish_time - start_time} seconds")

        return response
        """

    def get_base_html_template(self):
        """base.html 模板"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}{% endblock %}</title>
    <!-- Element Plus 样式 -->
    <link
            rel="stylesheet"
            href="https://unpkg.com/element-plus@2.8.7/dist/index.css"
    />
    <!-- Vue 3 -->
    <script src="https://unpkg.com/vue@3.5.12/dist/vue.global.js"></script>
    <!-- Import component library -->
    <script src="https://unpkg.com/element-plus@2.8.7/dist/index.full.js"></script>
    <script src="https://unpkg.com/axios@1.7.7/dist/axios.min.js"></script>
    <script src="https://unpkg.com/js-cookie@3.0.5/dist/js.cookie.min.js"></script>
    <script src="//unpkg.com/@element-plus/icons-vue"></script>

    {% block script_block %}
    {% endblock %}
    <style>
        body {
            font-family: Verdana;
            font-size: 15px;
            line-height: 1.5;
            color: #606266;
        }

        a {
            color: #000;
            text-decoration: none;
        }

        a:hover {
            color: #F00;
        }
    </style>
    {% block style_block%}
    {% endblock %}
</head>
<body>
<div id="main">
<!--    {% include 'common/header.html' %}-->
    {% block body_block %}
    {% endblock %}
<!--    {% include 'common/footer.html' %}-->
</div>
</body>
<script>
    let inactivityTime = 0
    let inactivityInterval
    let intervalSeconds = 7
    const maxInactiveTime = 1000 * 60 * 30

    const resetInactivityTimer = () => {
        // console.log('重置计时器')
        clearInterval(inactivityInterval)
        inactivityTime = 0
        startInactivityTimer()
    }

    const checkInactivity = async () => {
        inactivityTime += 1000 * intervalSeconds
        if (inactivityTime >= maxInactiveTime) {
            try {
                //
            } catch (error) {
                this.$message.error(error)
            }
        }
    }

    const startInactivityTimer = () => {
        // console.log('开启计时')
        inactivityInterval = setInterval(checkInactivity, 1000 * intervalSeconds)
    }

    startInactivityTimer()
</script>
{% block scripts %}
{% endblock %}
</html>
        """

    def get_index_html_template(self):
        """index.html 模板"""
        return """{% extends 'base.html' %}

{% block body_block %}
<h1>首页</h1>
{% endblock %}
        """

    def get_header_html_template(self):
        """header.html 模板"""
        return """<style>
    #nav {
        border-bottom: 3px solid #E10001;
        width: 1400px;
        height: 25px;
        background: #eee;
        margin: 0px auto;
    }
    #nav ul {
        /* overflow: hidden; */
        list-style: none;
        margin: 0px;
        padding: 0px;
    }
    #nav ul li {
        float: left;
        margin-left: 35px;
    }
    /* 将超链接设置成块元素更美观 */
    #nav ul li a {
        display: block;
        padding: 0px auto;
        width: 120px;
        height: 25px;
        line-height: 25px;
        text-align: center;
        font-size: 15px;
    }
    #nav ul li a:hover {
        background: #333;
        color: #fff;
    }
    #nav ul li ul {
        border: 1px solid #ccc;
        display: none;
        position: absolute;
    }
    #nav ul li ul li {
        float: none;
        width: 110px;
        background: #eee;
        margin: 0 auto;
    }
    #nav ul li ul li a {
        background: none;
    }
    #nav ul li ul li a:hover {
        background:#333;
        color: #fff;
    }
    #nav ul li:hover ul {
        display: block;
    }
</style>
<nav id="nav">
    <ul>
        <li><a href="#">首页</a></li>
    </ul>
</nav>
        """

    def get_footer_html_template(self):
        """footer.html 模板"""
        return """<style>
    #footer {
        margin: 0px auto;
    }
    #footer p {
        color: #879;
    }
</style>
<footer id="footer">
    <div class="icp">
        <p>这是 ICP 信息</p>
    </div>
</footer>
        """

    def create_project(self, project_name, databases=None, env_path=None, install_mirrors=None):
        """创建项目结构"""
        project_path = Path(project_name)

        if project_path.exists():
            print(f'错误: 项目目录「{project_name}」已存在!')
            return False

        print(f'正在创建项目:「{project_name}」')
        self._create_structure(project_path, self.project_structure, databases)

        # 更新配置文件中的数据库配置
        if databases:
            self._update_config_with_databases(project_path, databases)

        print(f'✅ 项目:「{project_name}」创建成功!')
        return project_path

    def _create_structure(self, base_path, structure, databases=None):
        """递归创建目录和文件结构"""
        for name, content in structure.items():
            path = base_path / name

            if isinstance(content, dict):
                # 创建目录
                path.mkdir(parents=True, exist_ok=True)
                self._create_structure(path, content, databases)
            else:
                # 创建文件
                with open(path, 'w', encoding='utf-8') as f:
                    # 如果是配置文件且指定了数据库, 需要特殊处理
                    if name == 'config.py' and databases:
                        f.write(self._generate_config_with_databases(content, databases))
                    elif name == 'README.md' and databases:
                        f.write(self._generate_readme_with_database(content, databases))
                    else:
                        f.write(content)

    def _generate_config_with_databases(self, base_config, databases):
        """生成包含指定数据库的配置文件"""
        config_lines = base_config.split('\n')
        new_config = []
        db_config = []
        yaml_config = []

        for db in databases:
            if db in DB_CONFIG_TEMPLATES:
                db_config.append(DB_CONFIG_TEMPLATES[db]['config'])
                yaml_config.append(DB_CONFIG_TEMPLATES[db]['yaml_template'])

        # 在适当位置插入数据库配置
        for line in config_lines:
            new_config.append(line)
            if 'pg_configs = config.get(' in line and 'postgres' not in databases:
                # 移除默认的PostgreSQL 配置
                continue
            if '# 数据库配置' in line:
                # 插入新的数据库配置
                new_config.extend(db_config)

        return '\n'.join(new_config)

    def _generate_readme_with_database(self, base_readme, databases):
        """生成包含指定数据库配置的 README"""
        yaml_template = """
app:
  host: 0.0.0.0
  port: 8000
  title: 服务名称
  description: 服务描述
        """

        for db in databases:
            if db in DB_CONFIG_TEMPLATES:
                yaml_template += DB_CONFIG_TEMPLATES[db]['yaml_template']

        # 替换 README 中的 YAML 配置身份
        readme_lines = base_readme.split('\n')
        new_readme = []
        in_yaml_section = False

        for line in readme_lines:
            if '```YAML' in line.upper():
                in_yaml_section = True
                new_readme.append(line)
                new_readme.extend(yaml_template.strip().split('\n'))
            elif '```' in line and in_yaml_section:
                in_yaml_section = False
                new_readme.append(line)
            elif not in_yaml_section:
                new_readme.append(line)

        return '\n'.join(new_readme)

    def _update_config_with_databases(self, project_path, databases):
        """配置文件中的数据库配置"""
        config_file = project_path / 'src' / 'app' / 'core' / 'config.py'
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 更新 TORTOISE_ORM 配置
            tortoise_orm_start = content.find('TORTOISE_ORM = {')
            if tortoise_orm_start != 1:
                models = ["'aerich.models'"]
                if 'postgres' in databases or 'mysql' in databases or 'sqlite' in databases:
                    models.insert(0, "'src.app.api.user_modules.models'")

                models_str = ',\n                    '.join(models)

                # 替换 models 部分
                new_tortoise_orm = f'''TORTOISE_ORM = {{
        "connections": {{
            "default": DATABASES.get("default", MYSQL_DATABASES.get("default", SQLITE_DATABASES.get("default")))
        }},
        "apps": {{
            "models": {{
                "models": [
                    {models_str},
                ],
                "default_connection": "default",
            }}
        }}
    }}
'''

                # 找到并替换 TORTOISE_ORM 部分
                tortoise_orm_end = content.find('}', tortoise_orm_start) + 1
                content = content[:tortoise_orm_start] + new_tortoise_orm + content[tortoise_orm_end:]

            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)

    def create_virtualenv(self, env_path):
        """创建虚拟环境"""
        try:
            env_path = Path(env_path)
            print(f'正在创建虚拟环境: {env_path}')

            import venv
            builder = venv.EnvBuilder(with_pip=True)
            builder.create(env_path)

            print(f'✅ 虚拟环境创建成功: {env_path}')
            return True
        except Exception as e:
            print(f'❌ 创建虚拟环境失败: {e}')
            return False

    def install_dependencies(self, project_path, env_path=None, mirror=None):
        """安装项目依赖"""
        requirements_file = project_path / 'requirements.txt'

        if not requirements_file.exists():
            print('❌ 未找到 requirements.txt 文件')
            return False

        pip_cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)]

        if mirror:
            mirror_url = MIRROR_MAP.get(mirror, mirror)
            pip_cmd.extend(['-i', mirror_url])
            print(f'使用镜像: {mirror_url}')

        if env_path:
            # 在虚拟环境中安装
            if sys.platform == 'win32':
                pip_path = Path(env_path) / 'Scripts' / 'pip.exe'
                python_path = Path(env_path) / 'Scripts' / 'python.exe'
            else:
                pip_path = Path(env_path) / 'bin' / 'pip'
                python_path = Path(env_path) / 'bin' / 'python'

            if pip_path.exists():
                pip_cmd[:3] = str(pip_path)
            else:
                pip_cmd[0] = str(python_path)

        print(f'正在安装依赖...')
        try:
            result = subprocess.run(pip_cmd, check=True, capture_output=True)
            print('✅ 依赖安装成功')
            return True
        except subprocess.CalledProcessError as e:
            print(f'❌ 依赖安装失败: {e}')
            print(f'错误输出: {e.stderr}')
            return False

    def create_app(self, project_name, app_name):
        """创建新的应用"""
        project_path = Path(project_name)
        if not project_path.exists():
            print(f'❌ 项目:「{project_name}」不存在')
            return False

        app_structure = {
            '__init__.py': '',
            'views.py': self.get_init_subapp_views_py_templdate(),
            'models.py': self.get_init_subapp_modesl_py_templdate(),
            'data_pydantic.py': self.get_init_subapp_data_pydantic_py_template(),
        }

        app_path = project_path / 'src' / 'app' / 'api' / app_name
        app_path.mkdir(parents=True, exist_ok=True)

        for filename, content in app_structure.items():
            file_path = app_path / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        print(f'✅ 应用模块 「{app_name}」创建成功')
        return True
