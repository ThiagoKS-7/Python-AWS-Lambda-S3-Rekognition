from boto3 import client
from pyparsing import Any

bucket_name = 'alura-bucket2'
file_name = '_analise.png'
coll_id = 'Faces'


def faceId_list(list):
    return [i['FaceId'] for i in list]


def find_matching_face(list):
    for face in list:
        return [{
            'id': face,
            'Matches': [
                {
                    'BoundingBox': res['Face']['BoundingBox'],
                    'Confidence': res['Face']['Confidence'],
                    'Name': (res['Face']['ExternalImageId']).capitalize(),
                }
            ]
        } for res in (client('rekognition')
                      .search_faces(
            CollectionId=coll_id,
            FaceId=face,
            MaxFaces=10,
            FaceMatchThreshold=80
        )['FaceMatches']
        )
        ]


def fa_handler(path) -> Any:
    try:
        client('s3').upload_file(
            Filename=path,
            Bucket=bucket_name,
            Key=file_name,
        )
        res = client('rekognition').index_faces(
            CollectionId=coll_id,
            DetectionAttributes=['DEFAULT'],
            ExternalImageId='temp',
            Image={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': file_name
                }
            }
        )
        client('s3').delete_object(Bucket=bucket_name, Key=file_name)
        return (
            find_matching_face(
                faceId_list([
                    {'BoundingBox': i['Face']['BoundingBox'],
                     'Confidence': i['Face']['Confidence'],
                     'FaceId': i['Face']['FaceId'],
                     }
                    for i in res['FaceRecords']
                ]
                )
            )
        )
    except Exception as e:
        return e


if __name__ == '__main__':
    print(fa_handler('data/temp.png'))
