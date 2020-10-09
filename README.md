## Aplicação de upload de arquivos com AWS S3, AWS Rekognition, AWS Lamba e AWS ECS

A aplicação foi desenvolvida utilizando o django juntamente com as tecnologias do Amazon AWS.

Os arquivos da aplicação estão armazenados em buckets no S3.Para isso, foram criados 3 buckets:

- **staticfilesatv:** contém os arquivos estáticos da aplicação (css, js, html, etc)
- **mediafiles:** contém os arquivos de upload
- **mediafilesresized:** arquivos gerados na função lambda.


### Função lambda

A função lambda é responsável por criar uma imagem redimensionado proporcionalmente( largura de 200px) a cada inserção no bucket 'mediafiles' e salvar no bucket 'mediafilesresized'. O arquivo de implantação da função está definido como 'function.zip' no diretório.

Segue implementação da função lambda

``` json
def resize_image(image_path, resized_path):
    with Image.open(image_path) as image:
        largura_desejada = 200
        largura_imagem = image.size[0]
        altura_imagem = image.size[1]
        percentual_largura = float(largura_desejada) / float(largura_imagem)
        altura_desejada = int((altura_imagem * percentual_largura))
        image = image.resize((largura_desejada, altura_desejada), Image.ANTIALIAS)
        image.save(resized_path)

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        tmpkey = key.replace('/', '')
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
        upload_path = '/tmp/{}'.format(tmpkey)
        s3_client.download_file(bucket, key, download_path)
        resize_image(download_path, upload_path)
        s3_client.upload_file(upload_path, 'mediafilesresized', key)
       
```


### Rekognition

A função do rekognition é idenfificar faces na imagem. Caso a função identifique faces, um bounding box é criado em cada face identificada e uma mensagem é mostrada com a provável idade da pessoa e o nível de confiança. Caso não há faces na imagem, é mostrada uma mensagem.



### Observações:

- Devido o limite máximo de requisições POST, PUT E LIST, apenas duas imagens são obtidas do bucket 'mediafiles' e o upload não é possível. Todas as outras funcionalidades(criar bucket, excluir bucket, upload de arquivos  e listagem de arquivos nos buckets e listagem dos buckets) estão como comentários no código para que não seja possível utilizarem.
- Criar os arquivos local_settings.py e local_credentials.py em /config e /bucket respectivamente. Esses dois arquivos contém as credenciais de acesso as apis do AWS.
- Foi necessário adicionar os nomes dos buckets e arquivos como hard-code devido a observação relatada no primeiro ítem.Normalmente, todos os buckets e seus arquivos são listados.
- Aplicação sendo executada em http://13.58.188.1:5000/





