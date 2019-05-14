import logging

from django.contrib.auth import get_user_model

from lazy_clients import LazyLoadedAuth0Client as Auth0Client


logger = logging.getLogger(__name__)


class Auth0UserModelMixin:
    def create_auth0_user(self):
        client = Auth0Client().get_client()

        if hasattr(self, 'agent') and self.agent:
            attributes = self.agent.attributes
            flex = dict(
                roles=attributes.get("roles", []),
                languages=attributes.get("languages", []),
                skills={
                    to_snake_case(agent_skill.skill.name): agent_skill.score
                    for agent_skill in self.skills.all()
                },
            )

        else:
            flex = dict(
                roles=[],
                languages=[],
                skills={},
            )

        payload = dict(
            connection="Initial-Connection",
            email=self.email,
            phone_number=self.phone_number,
            app_metadata=dict(flex=flex),
        )

        client.users.create(payload)
        return user

    def get_auth0_user(self):
        user = None
        uid = self.auth0_user_id
        email = self.email
        client = Auth0Client().get_client()

        if uid:
            user = client.users.get(uid)
            logger.info(f"fetched auth0 user:{user} by uid")
        else:
            user_queryset = client.users_by_email.search_users_by_email(email)
            if len(user_queryset) == 0:
                logger.info("No user with given email.")
            elif len(user_queryset) > 1:
                logger.info("More than one user with given email.")
            elif len(user_queryset) == 1:
                user = user_queryset[0]
                self.auth0_user_id = user["user_id"]
                self.image_url = user.get("picture")
                self.save()
            logger.info(f"fetched auth0 user:{user} by email")

        if not user:
            user = self.create_auth0_user()
            logger.info(f"created auth0 user:{user}")

        return user

    def synchronize_auth0(self):
        user = self.get_auth0_user()
        uid = user.get("uid")

        if not self.auth0_user_id:
            logger.warning(f"agent:{self.uuid} - setting auth id")
            self.auth0_user_id = uid
            self.save()

        if not self.image_url or self.image_url in [get_user_model().DEFAULT_IMAGE_URL, '', None]:
            logger.warning(f"agent:{self.uuid} - setting image_url")
            self.image_url = user.get("picture", get_user_model().DEFAULT_IMAGE_URL)
            self.save()

        client = Auth0Client().get_client()

        if hasattr(self, 'agent') and self.agent:
            attributes = self.agent.attributes
            app_metadata = dict(
                flex=dict(
                    sid=self.agent.twilio_worker_sid,
                    roles=attributes.get("roles", []),
                    languages=attributes.get("languages", []),
                    skills={},
                )
            )
        else:
            app_metadata = {}

        client.users.update(self.auth0_user_id, dict(app_metadata=app_metadata))

        return user
