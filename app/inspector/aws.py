# -*- coding: utf-8 -*-
import boto3


def get_aws_client(
    client_type,
    role_arn,
    role_session_name,
    region,
):
    """Helper function for getting an authenticated boto3 client.
    """
    sts = boto3.client('sts', region_name=region)
    assumed_role_object = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName=role_session_name,
    )
    credentials = assumed_role_object['Credentials']
    client = boto3.client(
        client_type,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
        region_name=region,
    )
    return client
