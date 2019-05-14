import logging

from django.conf import settings

from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0
from twilio.rest import Client as TwilioRestClient
import boto3


logger = logging.getLogger(__name__)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class LazyLoadedTwilioClient:
    __metaclass__ = Singleton

    client = None

    def get_client(self):
        if self.client is not None:
            return self.client

        twilio_logger = logging.getLogger("twilio.http_client")
        twilio_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
        self.client = TwilioRestClient(
            username=settings.TWILIO_ACCOUNT_SID, password=settings.TWILIO_AUTH_TOKEN
        )
        return self.client


class LazyLoadedAWSClient:
    __metaclass__ = Singleton

    bucket = None
    s3 = None

    def __init__(self, *args, **kwargs):
        self.bucket_name = settings.S3_BUCKET_NAME

    def get_s3(self):
        if self.s3 is not None:
            return self.s3

        s3 = boto3.resource("s3")
        self.s3 = s3
        return self.s3

    def get_bucket(self):
        if self.bucket:
            return self.bucket
        s3 = self.get_s3()
        bucket = s3.Bucket(self.bucket_name)
        return bucket


class LazyLoadedAuth0Client:
    __metaclass__ = Singleton

    def __init__(self, *args, **kwargs):
        self.domain = settings.AUTH0_DOMAIN

    def get_client(self):
        mgmt_api_token = self.get_token()
        auth0 = Auth0(self.domain, mgmt_api_token)
        return auth0

    def get_token(self):
        get_token = GetToken(self.domain)

        token = get_token.client_credentials(
            settings.AUTH0_CLIENT_ID,
            settings.AUTH0_CLIENT_SECRET,
            f"https://{self.domain}/api/v2/",
        )

        mgmt_api_token = token["access_token"]
        return mgmt_api_token
