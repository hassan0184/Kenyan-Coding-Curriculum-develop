import boto3

s3_client = boto3.client("s3")


def upload_file_to_s3(file_name, key, bucket="edmazingbucket", s3_client_obj=s3_client):
    return s3_client_obj.upload_file(
        Filename=file_name,
        Bucket=bucket,
        Key=key)


def download_file_from_s3(file_name, key, bucket="edmazingbucket", s3_client_obj=s3_client):
    return s3_client_obj.download_file(Bucket=bucket, Key=key, Filename=file_name)


def get_file_url(key,bucket_name="edmazingbucket" ,s3_client_obj=s3_client):
    url = s3_client_obj.generate_presigned_url(
    ClientMethod='get_object',
    Params={
        'Bucket': bucket_name,
        'Key': key
    })
    return url
