import logging
import boto3
from botocore.exceptions import ClientError


class AwsS3UploadClass:
    def __init__(self, id_key, secret_key, bucket_name):
        """
        AWS S3 Upload Class

        Arguments:
            * id_key (string) aws access key id
            * secret_key (string) aws secret access key
            * bucket (string) the S3 Bucket to connect to
        Attributes:
            * bucket (S3.Bucket) the bucket instance for the specified `bucket_name`
        """

        self.id_key = id_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name

        self.client = boto3.client('s3', endpoint_url=None, aws_access_key_id=self.id_key,
                                   aws_secret_access_key=self.secret_key, region_name='eu-central-1')

    def get_bucket(self, bucket_name):
        try:
            bucket = self.client.get_bucket(bucket_name)
        except ClientError as e:
            bucket = None
        return bucket

    def create_presigned_post(self, object_name, fields=None, conditions=None, expiration=3600):
        """Generate a presigned URL S3 POST request to upload a file
        :param bucket_name: string
        :param object_name: string
        :param fields: Dictionary of prefilled form fields
        :param conditions: List of conditions to include in the policy
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Dictionary with the following keys:
            url: URL to post to
            fields: Dictionary of form fields and values to submit with the POST
        :return: None if error.
        """

        try:
            response = self.client.generate_presigned_post(
                self.bucket_name, object_name, Fields=fields, Conditions=conditions, ExpiresIn=expiration)
        except ClientError as e:
            logging.error(e)
            return None
        return response