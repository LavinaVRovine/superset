# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# This file is included in the final Docker image and SHOULD be overridden when
# deploying the image to prod. Settings configured here are intended for use in local
# development environments. Also note that superset_config_docker.py is imported
# as a final step as a means to override "defaults" configured here
#
import logging
import os
from datetime import timedelta
from typing import Optional

from cachelib.file import FileSystemCache
from celery.schedules import crontab

logger = logging.getLogger()


def get_env_variable(var_name: str, default: Optional[str] = None) -> str:
    """Get the environment variable or raise exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        else:
            error_msg = "The environment variable {} was missing, abort...".format(
                var_name
            )
            raise EnvironmentError(error_msg)


DATABASE_DIALECT = get_env_variable("DATABASE_DIALECT")
DATABASE_USER = get_env_variable("DATABASE_USER")
DATABASE_PASSWORD = get_env_variable("DATABASE_PASSWORD")
DATABASE_HOST = get_env_variable("DATABASE_HOST")
DATABASE_PORT = get_env_variable("DATABASE_PORT")
DATABASE_DB = get_env_variable("DATABASE_DB")

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = "%s://%s:%s@%s:%s/%s" % (
    DATABASE_DIALECT,
    DATABASE_USER,
    DATABASE_PASSWORD,
    DATABASE_HOST,
    DATABASE_PORT,
    DATABASE_DB,
)

REDIS_HOST = get_env_variable("REDIS_HOST")
REDIS_PORT = get_env_variable("REDIS_PORT")
REDIS_CELERY_DB = get_env_variable("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = get_env_variable("REDIS_RESULTS_DB", "1")

RESULTS_BACKEND = FileSystemCache("/app/superset_home/sqllab")

CACHE_CONFIG = {
    "CACHE_TYPE": "redis",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": REDIS_RESULTS_DB,
}
DATA_CACHE_CONFIG = CACHE_CONFIG


class CeleryConfig(object):
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    imports = ("superset.sql_lab",)
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    worker_prefetch_multiplier = 1
    task_acks_late = False
    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=10, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig

FEATURE_FLAGS = {
        "ALERT_REPORTS": True,
        "DASHBOARD_NATIVE_FILTERS": True,
        "DASHBOARD_CROSS_FILTERS": True


}
ALERT_REPORTS_NOTIFICATION_DRY_RUN = True
WEBDRIVER_BASEURL = "http://superset:8088/"
# The base URL for the email report hyperlinks.
WEBDRIVER_BASEURL_USER_FRIENDLY = WEBDRIVER_BASEURL

SQLLAB_CTAS_NO_LIMIT = True



from flask_appbuilder.security.manager import (
    # AUTH_DB,
    # AUTH_LDAP,
    AUTH_OAUTH,
    # AUTH_OID,
    # AUTH_REMOTE_USER
)
import os

CLIENT_ID = os.getenv('auth_0_client_id', "alsrFiaw6GkhYBelPdfi8EpeankiDkLL")
CLIENT_ID = "7q2F5bnqcnds7xwfymRB4topKiRno26t"
CLIENT_SECRET = os.getenv('auth_0_client_secret', "levDVnS3zVlmDzQlzWl3HDfEyr1CC5F01k6xJ2G8DlrwMQJ_CZEHGJGmrJtPncve")
CLIENT_SECRET = "xsmipZu2uwxYmNEvlbouljQEW3mZ9PWO4rRE5XNMkQps2j2eEhmcrSUY3L1Qr3Xm"
TENANT = os.getenv('auth_0_tenant', "logex-nl-test.eu.auth0.com")
TENANT = "logex-uk-test.eu.auth0.com"
api_base_url = f"https://{TENANT}"
AUTH_TYPE = AUTH_OAUTH
OAUTH_PROVIDERS = [
    {   'name':'auth0',
        'token_key':'access_token', # Name of the token in the response of access_token_url
        'icon':'fa-address-card',   # Icon for the provider
        'remote_app': {
            'client_id':CLIENT_ID,  # Client Id (Identify Superset application)
            'client_secret':CLIENT_SECRET, # Secret for this Client Id (Identify Superset application)
            'client_kwargs':{
                'scope': "openid email profile"              # Scope for the Authorization
            },
            'access_token_method':'POST',    # HTTP Method to call access_token_url
            'access_token_params':{        # Additional parameters for calls to access_token_url
                'client_id':CLIENT_ID
            },
            'access_token_headers':{    # Additional headers for calls to access_token_url
                'Authorization': 'Basic Base64EncodedClientIdAndSecret'
            },
            'api_base_url':api_base_url,
            'access_token_url':f'{api_base_url}/oauth/token',
            'authorize_url':f"{api_base_url}/authorize",
            'server_metadata_url': api_base_url + '/.well-known/openid-configuration',

        }
    }
]

# Will allow user self registration, allowing to create Flask users from Authorized User
AUTH_USER_REGISTRATION = True

# Map Authlib roles to superset roles
AUTH_ROLE_ADMIN = 'Admin'
AUTH_ROLE_PUBLIC = 'Public'

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "Admin"
LOG_LEVEL = "DEBUG"

from custom_sso_security_manager import CustomSsoSecurityManager
CUSTOM_SECURITY_MANAGER = CustomSsoSecurityManager



# Optionally import superset_config_docker.py (which will have been included on
# the PYTHONPATH) in order to allow for local settings to be overridden
#
try:
    import superset_config_docker
    from superset_config_docker import *  # noqa

    logger.info(
        f"Loaded your Docker configuration at " f"[{superset_config_docker.__file__}]"
    )
except ImportError:
    logger.info("Using default Docker config...")
