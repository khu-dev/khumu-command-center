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

## 개발 팁

* pip dependency
  ```bash
  $ pip freeze > requirements.txt
  # requirements.txt 작성 후 pkg-resources==0.0.0 line을 지워준다. 
  ```

* mysqlclient dependency - MySQL을 이용하기 위해서 필요한 ubuntu의 패키지들이다.
  * `sudo apt-get install python3-dev`
  * `sudo apt-get install libmysqlclient-dev`
    * 일반 ubuntu에서는 `libmysqlclient-dev`, python ubuntu container에서는 `default-libmysqlclient-dev`(?). 아마 후자로만 해도 될 것 같음.
  * `pip install mysqlclient`
  * `pip install wheel`

* 다양한 환경에 따른 config
  * `KHUMU_ENVIRONMENT` 값을 통해 설정 가능 (`local` | `dev`, default는 `local`)
  * `KHUMU_ENVIRONMENT` 의 값에 따라`config/local.yaml` 혹은 `config/dev.yaml` 를 이용해 `settings.py` 에서 각종 설정을 동적으로 취한다.
