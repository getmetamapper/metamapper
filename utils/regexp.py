# -*- coding: utf-8 -*-
import re
"""
IPv4 address (e.g., 127.0.0.1)
"""
IPV4_PATTERN = (r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}'
                r'([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')

ipv4_regex = re.compile(IPV4_PATTERN, re.IGNORECASE)
"""
Domain host (e.g., app.skiplogic.io || www.google.com)
"""
HOST_PATTERN = (r'^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*'
                r'([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$')

host_regex = re.compile(HOST_PATTERN, re.IGNORECASE)
"""
Domain (e.g., app.skiplogic.io || www.google.com)
"""
DOMAIN_PATTERN = (r'^[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,6}$')

domain_regex = re.compile(DOMAIN_PATTERN, re.IGNORECASE)
"""
URL Regular Expression (e.g., https://app.skiplogic.io?email=smc@gmail.com)
"""
URL_PATTERN = (r'^(?:http|ftp)s?://'
               r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
               r'localhost|'
               r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
               r'(?::\d+)?'
               r'(?:/?|[/?]\S+)$')

url_regex = re.compile(URL_PATTERN, re.IGNORECASE)
"""
Universally unique identifier (UUID) (e.g., f5ab2db8-9f42-48aa-a01b-195ac26bbb36)
"""
UUID_PATTERN = r'^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$'

uuid_regex = re.compile(UUID_PATTERN)
"""
SkipLogic PK identifier (e.g., f65Axab51bA8)
"""
STR_PK_PATTERN = r'^[a-zA-Z0-9]{12}$'

str_pk_regex = re.compile(STR_PK_PATTERN)
"""
Email address (e.g., scott@skiplogic.io)
"""
EMAIL_PATTERN = r'[^@]+@[^@]+\.[^@]+'

email_regex = re.compile(EMAIL_PATTERN, re.IGNORECASE)
"""
x509 certificate
"""
X509_CERT_PATTERN = r'(-+BEGIN CERTIFICATE-+)((.|\n)*?)(-+END CERTIFICATE-+)'

x509_cert_regex = re.compile(X509_CERT_PATTERN, re.IGNORECASE)
"""
Phone Number
"""
PHONE_PATTERN = r'^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$'

phone_regex = re.compile(PHONE_PATTERN, re.IGNORECASE)
"""
Metamapper Domain Verification
"""
DOMAIN_VERIFICATION = r'^"?(metamapper-domain-verification)=([a-zA-Z0-9]+)"?$'

domain_verification_regex = re.compile(DOMAIN_VERIFICATION, re.IGNORECASE)
"""
JSON Web Token
"""
JSON_WEB_TOKEN = r'^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$'

jwt_regex = re.compile(JSON_WEB_TOKEN)
