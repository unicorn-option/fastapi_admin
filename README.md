# FastAPI Admin CLI

一个用于快速创建 FastAPI 项目的命令行工具。

## 安装

```bash
pip install fastapi-cli
```

## 使用方法

### 创建新项目

```bash
# 交互式创建项目
$ fastapi-cli create-project -n myproject

# 创建项目并自动创建虚拟环境
$ fastapi-cli create-project -n myproject -e

# 创建项目并指定数据库和镜像
$ fastapi-cli create-project -n myproject -e -i tuna -d postgres,redis
```

### 创建应用模块

```bash
$ fastapi-cli create-app myproject product_module
```

### 命令详解

#### create-project 命令

| 参数 | 简写 | 说明             |
| -- | -- |----------------|
| --name | -n | 项目名称 (必要) |
| --env | e | 创建虚拟环境 (可选) |
| -install | -i | 安装依赖并指定镜像 (可选) |
| --databases | -d | 指定数据库配置 (可选) |

#### create-app 命令

| 参数 | 说明 |
| -- | -- |
| project_name | 项目名称 (必要) |
| app_name | 应用模块名称 (必要) |

#### 支持的数据库

- postgres: PostgreSQL 数据库
- mysql: MySQL 数据库
- redis: Redis 缓存
- sqlite: SQLite 数据库

#### 支持的镜像源

- default: 官方 PyPi
- tuna: 清华镜像源
- aliyun: 阿里云源
- 待补充

### 开发

```bash
# 从源码安装
git clone https://github.com/unicorn-option/fastapi_admin.git
cd fastapi_admin
pip install -e .

# 打包
python setup.py sdist bdist_wheel

# 上传到 PyPI
twine upload dist/*
```

## 功能特性

- 🚀 快速创建 FastAPI 项目结构
- 🔧 自动虚拟环境管理
- 📦 依赖包自动安装
- 🗄️ 多数据库配置支持
- 🎯 模块化应用创建
- ⚙️ 交互式配置选项

## 许可证 

MIT License
