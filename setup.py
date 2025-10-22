from setuptools import setup, find_packages

# 读取 README.md 作为长描述
with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

# 读取 requirements.txt
with open("requirements.txt", "r", encoding='utf-8') as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name='fastapi-admin',
    version='0.1.0',
    author='unicorn',
    author_email='unicorn_0618@foxmail.com',
    description='A CLI tool for creating FastAPI project scaffolding\n一个创建初始化 FastAPI 项目的命令行工具',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/unicorn-option/fastapi_admin.git',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "fastapi_admin": ['templates/*.py', 'templates/*.md', 'templates/*.html', 'templates/*.yml'],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "fastapi-cli=fastapi_cli.cli:main",
        ],
    },
    keywords="fastapi, cli, scaffold, project-template",
    project_urls={
        "Bug Reports": "https://github.com/unicorn-option/fastapi_admin/issues",
        "Source": "https://github.com/unicorn-option/fastapi_admin.git",
    },
)
