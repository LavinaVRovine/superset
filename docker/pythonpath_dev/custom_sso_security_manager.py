from superset.security import SupersetSecurityManager
from jose import jwt
from requests import request
import logging

f_logger = logging.getLogger()

class CustomSsoSecurityManager(SupersetSecurityManager):
    def request(self, url, method="GET", *args, **kwargs):
        f_logger.fatal("AAA")
        kwargs.setdefault("headers", {})
        response = request(method, url, *args, **kwargs)
        response.raise_for_status()
        return response

    def get_jwks(self, url, *args, **kwargs):
        f_logger.fatal("bbb")
        return self.request(url, *args, **kwargs).json()

    def get_oauth_user_info(self, provider, response=None):
        f_logger.fatal("ccc")
        if provider == "auth0":
            f_logger.fatal("ddd")
            # fing thanks to https://stackoverflow.com/questions/71532060/apache-superset-and-auth0-returns-the-browser-or-proxy-sent-a-request-that-th
            id_token = response["id_token"]
            metadata = self.appbuilder.sm.oauth_remotes[provider].server_metadata
            jwks = self.get_jwks(metadata["jwks_uri"])
            audience = self.appbuilder.sm.oauth_remotes[provider].client_id
            payload = jwt.decode(
                id_token,
                jwks,
                algorithms=["RS256"],
                audience=audience,
                issuer=metadata["issuer"],
            )
            first_name, last_name = payload["name"].split(" ", 1)
            return {
                "email": payload["email"],
                "username": payload["email"],
                "first_name": first_name,
                "last_name": last_name,
            }
        return super().get_oauth_user_info(provider, response)

    # def oauth_user_info(self, provider, response=None):
    #     logging.debug("Oauth2 provider: {0}.".format(provider))
    #     if provider == 'auth0':
    #         # As example, this line request a GET to base_url + '/' + userDetails with Bearer  Authentication,
    # # and expects that authorization server checks the token, and response with user details
    #         try:
    #             from authlib.integrations.flask_client.apps import FlaskOAuth2App
    #             provider_x:FlaskOAuth2App = self.appbuilder.sm.oauth_remotes[provider]
    #             # logger.warning(
    #             #     self.appbuilder.sm.oauth_remotes[provider].items()
    #             # )
    #             # return {'name': "p", 'email': "pavel.kalmmert@logex.com", 'id': "pavel",
    #             #         'username': 'pavel', 'first_name': '', 'last_name': ''}
    #             me = provider_x.get('userinfo')
    #         except BaseException:
    #             return {}
    #         logging.debug("user_data: {0}".format(me))
    #         return {'name': me['name'], 'email': me['email'], 'id': me['user_name'],
    #                 'username': me['user_name'], 'first_name': '', 'last_name': ''}
    # ...
