"""
数据库配置模板
"""

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
  user: your_postgres_user
  password: your_postgres_password
  db: your_database_name
"""
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
  user: your_mysql_user
  password: your_mysql_password
  db: your_database_name
"""
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
  password: your_redis_password
"""
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
"""
    }
}
