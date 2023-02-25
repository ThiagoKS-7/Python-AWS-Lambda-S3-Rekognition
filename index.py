from boto3 import resource, client
import logging

datestr = "%d/%m/%Y %I:%M:%S %p"
fmtstr = "%(asctime)s - %(levelname)s: %(funcName)s() \
Line: %(lineno)d %(message)s"

logging.basicConfig(
    filename="output.log",
    level=logging.INFO,
    filemode="w",
    format=fmtstr,
    datefmt=datestr
)


def list_images():
    return [
        i.key for i in
        resource('s3').Bucket('alura-bucket2').objects.all()
    ]


def list_collections():
    return (client('rekognition')
            .list_collections(MaxResults=2)
            ['CollectionIds']
            )


def index_collection(images):
    print(images)
    try:
        if 'Faces' in list_collections():
            for i in images:
                client('rekognition').index_faces(
                    CollectionId='Faces',
                    DetectionAttributes=[],
                    ExternalImageId=i[:-4],
                    Image={
                        'S3Object': {
                            'Bucket': 'alura-bucket2',
                            'Name': i
                        }
                    }
                )
            logging.info("Collection Faces indexed successfully!")
        else:
            response = (client('rekognition')
                        .create_collection(CollectionId='Faces')
                        )
            print('Collection ARN: ' + response['CollectionArn'])
            print('Status code: ' + str(response['StatusCode']))
            logging.info("Collection Faces created successfully!")
    except Exception as e:
        logging.info("Request failed!", e)
        return e


if __name__ == '__main__':
    index_collection(list_images())
