from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """This app is only an extension to the account management from django-allauth."""
    name = 'receval.apps.accounts'

    def ready(self):
        from receval.apps.accounts import signals

        # Do something with imports so it does not get flagged as "unused import".
        if signals.create_auth_token:
            pass
