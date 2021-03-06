import io
import json
import os
import random

import boto3
from PIL import Image, ImageDraw
from botocore.config import Config
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.base import View

from . import local_credentials


class Base(View):

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        self.session = boto3.Session(

            aws_access_key_id=local_credentials.aws_access_key_id,
            aws_secret_access_key=local_credentials.aws_secret_access_key,
            region_name='us-east-2',
        )
        self.s3 = self.session.client('s3', region_name='us-east-2',
                                      config=Config(signature_version='s3v4')
                                      )
        # necessário definir hard-code devido o limite de solicitações
        self.bucket_name = 'mediasfiles'


class RekognitionImage(Base):

    def get(self, *args, **kwargs):
        if self.request.is_ajax:
            file_name = self.request.GET.get('file', None)
            # bucket_name = self.request.GET.get('bucket_name', None)

            obj_s3 = self.s3.get_object(
                Bucket=self.bucket_name,
                Key=file_name,
            )

            img = obj_s3['Body'].read()

            client = boto3.client('rekognition', aws_access_key_id=local_credentials.aws_access_key_id,
                                  aws_secret_access_key=local_credentials.aws_secret_access_key,
                                  region_name='us-east-2', )

            response = client.detect_faces(Image={'Bytes': img}, Attributes=['ALL'])

            stream = io.BytesIO(img)
            image = Image.open(stream)

            imgWidth, imgHeight = image.size
            draw = ImageDraw.Draw(image)

            result = {}

            for x, faceDetail in enumerate(response['FaceDetails']):
                color = "#%06x" % random.randint(0, 0xFFFFFF)
                result[color] = f"A pessoa tem entre {str(faceDetail['AgeRange']['Low'])} a " \
                                f" {str(faceDetail['AgeRange']['High'])} anos de idade com um nível de " \
                                f"confiança de {'%.4f' % faceDetail['Confidence']}%"

                box = faceDetail['BoundingBox']
                left = imgWidth * box['Left']
                top = imgHeight * box['Top']
                width = imgWidth * box['Width']
                height = imgHeight * box['Height']

                points = (
                    (left, top),
                    (left + width, top),
                    (left + width, top + height),
                    (left, top + height),
                    (left, top)
                )
                draw.line(points, fill=color, width=3)
            ext = file_name.split('.')[-1]
            tp = os.path.join(settings.MEDIA_ROOT, f'reconhecimento.{ext}')

            image.save(tp)

            if len(result) == 0:
                result['black'] = 'Nenhum rosto identificado'
            response = {
                'result': result,
                'img': os.path.join(settings.MEDIA_URL, f'reconhecimento.{ext}')
            }

            return HttpResponse(
                json.dumps(response),
                content_type="application/json"
            )


class Index(Base):

    def get(self, *args, **kwargs):
        # modificação devido limite no s3
        '''bucket_name = self.kwargs.get('bucket', None)
        response = self.s3.list_objects(
            Bucket='mediasfiles',
        )
        return render(self.request, 'bucket/buckets_list_files.html', {'files': response.get('Contents'),
                                                                       'bucket_name': bucket_name,
                                                                       }
                      )'''

        file_1 = self.s3.get_object(
            Bucket=self.bucket_name,
            Key='download.jpeg'
        )
        file_2 = self.s3.get_object(
            Bucket=self.bucket_name,
            Key='1.png'
        )
        response_1 = {
            'Key': 'download.jpeg',
            'LastModified': file_1['LastModified'],
            'Size': len(file_1['Body'].read())

        }
        response_2 = {
            'Key': '1.png',
            'LastModified': file_2['LastModified'],
            'Size': len(file_2['Body'].read())

        }
        response = []
        response.append(response_1)
        response.append(response_2)

        return render(self.request, 'bucket/buckets_list_files.html', {'files': response,
                                                                       'bucket_name': self.bucket_name,
                                                                       })

    '''def post(self, *args, **kwargs):
        bucket_name = self.request.POST.get('bucket_name', None)
        if bucket_name is not None:
            try:
                self.s3.create_bucket(Bucket=bucket_name,
                                      CreateBucketConfiguration={
                                          'LocationConstraint': 'us-east-2'
                                      },
                                      )
                messages.info(self.request, 'Bucket adicionado!')

            except Exception:
                messages.error(self.request, 'Nome do bucket inválido')

        return redirect('bucket:index')'''


'''class DeleteBucket(Base):
    def get(self, *args, **kwargs):
        bucket_name = self.kwargs.get('bucket', None)
        if bucket_name is not None:
            objects = self.s3.list_objects(
                Bucket=bucket_name,
            )
            if objects.get('Contents', None) is not None:
                for obj in objects['Contents']:
                    self.s3.delete_object(Bucket=bucket_name, Key=obj['Key'])

            self.s3.delete_bucket(
                Bucket=bucket_name,
            )
            messages.success(self.request, 'Bucket removido com sucesso!')
        else:
            messages.success(self.request, 'Erro ao remover o Bucket!')

        return redirect('bucket:index')'''

'''class ShowBucket(Base):
    def get(self, *args, **kwargs):
        bucket_name = self.kwargs.get('bucket', None)
        response = self.s3.list_objects(
            Bucket=bucket_name,
        )
        return render(self.request, 'bucket/buckets_list_files.html', {'files': response.get('Contents'),
                                                                       'bucket_name': bucket_name,
                                                                       }
                      )'''


class DownloadFile(Base):
    def get(self, *args, **kwargs):
        if self.request.is_ajax:
            file_name = self.request.GET.get('file', None)
            bucket_name = self.request.GET.get('bucket', None)

            response = self.s3.generate_presigned_url('get_object',
                                                      Params={'Bucket': bucket_name,
                                                              'Key': file_name,

                                                              },
                                                      )
            response = {
                'url': response
            }
            return HttpResponse(
                json.dumps(response),
                content_type="application/json"
            )


class DeleteFile(Base):
    def get(self, *args, **kwargs):
        file_name = self.kwargs.get('file', None)
        bucket_name = self.kwargs.get('bucket', None)
        self.s3.delete_object(
            Bucket=bucket_name,
            Key=file_name,
        )
        messages.info(self.request, 'Arquivo removido!')

        return redirect('bucket:show_bucket', bucket=bucket_name)


'''class UploadFile(Base):
    def post(self, *args, **kwargs):
        bucket_name = self.request.POST.get('bucket', None)
        files = self.request.FILES
        try:
            if os.path.exists(settings.MEDIA_ROOT) is False:
                print(settings.MEDIA_ROOT)
                os.mkdir(settings.MEDIA_ROOT)
            for f in files.getlist('file'):
                path = default_storage.save(str(f), ContentFile(f.read()))
                tmp_file = os.path.join(settings.MEDIA_ROOT, path)
                self.s3.upload_file(tmp_file, bucket_name, str(f))
                os.remove(tmp_file)

            messages.info(self.request, 'Arquivos(s) adicionado(s)')
        except:
            messages.error(self.request, 'Arquivos inválidos!')
        return redirect('bucket:show_bucket', bucket=bucket_name)'''
