# KHUMU

Django REST Framework을 바탕으로한 REST API 서버

## How to run the server

```bash
$ pip install -r requirements.txt
$ python manage.py runserver
```

## Docker을 이용해 개발 환경 구축하기

### khumu-command-center만 이용하는 경우

```bash
$ docker run -t --rm --name tmp -v $PWD:/khumu -p 8000:8000 tmp
```

* -t 옵션을 설정하지 않으면 terminal output이 제대로 출력되지 않는 경우가 있더라.
* python package의 의존성이 변경되면 이미지 빌드를 새로해주어야한다.

### How to build the image

```bash
docker build -f Dockerfile-dev . -t ${{ IMAGE_NAME }}
``` 