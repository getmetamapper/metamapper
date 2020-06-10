# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management.commands import loaddata

from app.authentication.models import User


X509CERT = '''
-----BEGIN CERTIFICATE-----
MIIDCzCCAfOgAwIBAgIJZC/zKbXIzEkcMA0GCSqGSIb3DQEBCwUAMCMxITAfBgNV
BAMTGG1ldGFtYXBwZXItZGV2LmF1dGgwLmNvbTAeFw0xOTAyMTUwMzUwNDFaFw0z
MjEwMjQwMzUwNDFaMCMxITAfBgNVBAMTGG1ldGFtYXBwZXItZGV2LmF1dGgwLmNv
bTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMOUfc2AWAJN7Fv+wZ+R
+9CLN3ewimd++0TqV2wIo72Ud/PKM03kfODkWxKwqCHw6j2YZWugbjtmvS7pm/93
k3PyyjuOybBawd5IiMw8XAVFvTRmkREl26bwuHFOwWFv7DHpTjbs4cgxm++2Jcx1
7DgrRIJUpOKjwpFs+kGnlWReTNseF7RAhDTe/7BcArYGdrwVE3nafbGluiZBtjti
dD7J1YxnRPep0GaezjRtI6ygxliKDUU3iBwR4k8uCEj3XFjN+UutwgK318SFU2B0
rXb1UmIhtpV7ePxYmEKh9A+H8xFclGfiMd1FFQ4eH1PfAOM1ljIzDsKhNJUNnR0P
X80CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUtszg6c0bozrL
T/cZiqU62gfjwWwwDgYDVR0PAQH/BAQDAgKEMA0GCSqGSIb3DQEBCwUAA4IBAQA0
+l+P419AOY88ZFjXhjXM9S0d+4hIKLAg9Yb7tfPs8l4lIEGQnWxvO3XrrPeKfzwf
mH1H178gs08xsvZvamQVzMMGjwipOosftxPzpm1xmqVP24tXi7YMbSzIjXzuqCIC
XuFYaddZm8A+ToZ7tt91uGoXeR6AvSKgYyt0bncgSCYeTkVUuHji3Jq49TfPYvni
zRUvCAe7TGKcrEyolRTlYN+fVFSRLbyv8PryAun9mkMAxb/PnmesajqyEG82oaRr
bDHfQIPd6BoOTXRyGJD0Ys+SK/GyV4+yykCeAY31kRxnQPZuxVBkgolQxIFa5CSy
8XfmMm8dVx3C2RByNCPJ
-----END CERTIFICATE-----
'''

SSO_URL = "https://metamapper-dev.auth0.com/samlp/DPu0xf39ViVfB6UWMv5x97uiTBtEuVfV"
SLO_URL = None
ENTITY_ID = "urn:metamapper-dev.auth0.com"


class Command(loaddata.Command):
    """Overrides loaddata command to add MM-specific logic.
    """
    help = 'Seed local database with sample data'

    def handle(self, *args, **options):
        if not settings.DJANGO_ENV == 'development':
            self.stdout.write('Can only execute command in development environment.')
            return

        super().handle(*args, **options)

        users = User.objects.all()

        for user in users:
            if not user.password == 'password1234':
                continue
            user.set_password("password1234")
            user.save()
            self.stdout.write(self.style.SUCCESS('Successfully updated "%s"' % user.email))
