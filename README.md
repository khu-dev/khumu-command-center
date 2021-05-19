# KHUMU

Django REST Framework을 바탕으로한 REST API 서버

## API Documentation

**[API Documentation](https://documenter.getpostman.com/view/13384984/TVsvfkxs)**

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
$ docker build -f Dockerfile-dev . -t ${{ IMAGE_NAME }}
```

### How to initiate the data

```bash
$ make init
```

DB와 연결 되어있는 지 체크 후 초기화할 것.

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
  * `KHUMU_ENVIRONMENT` 값을 통해 설정 가능 (`LOCAL` | `DEV`, default는 `LOCAL`)
  * `KHUMU_ENVIRONMENT` 의 값에 따라`config/local.yaml` 혹은 `config/dev.yaml` 를 이용해 `settings.py` 에서 각종 설정을 동적으로 취한다.

## Install chrome driver

인포 21 인증을 위해 Selenium과 chrome driver를 사용한다. chrome driver는 project root에 위치해야한다.

```shell
curl https://chromedriver.storage.googleapis.com/89.0.4389.23/chromedriver_linux64.zip -o chromedriver.zip && unzip chromedriver.zip
```

## Entities

### Article

커뮤니티 게시판의 게시물

### LikeArticle

게시물에 대한 좋아요

### BookmarkArticle

게시물에 대한 북마크

### Board

community tab에 존재하는 게시판들.

![image-20210516155058970](/home/jinsu/.config/Typora/typora-user-images/image-20210516155058970.png)

* category - 하단의 (`official` | `department` | `lecture` | `free`)

### (예정) StudyBoard

Board를 상속

* category - (`lecture` | `civil(공무원)` | `certificate(자격증)` | `career(취준)`)

### (예정) AnnouncementBoard

Board를 상속

category - (`university` | `khumu(쿠뮤의 공지사항 - 필요할까? ㅋㅋㅋ 그냥 어디 따로 띄우는 게 낫지 않으려나)` | `council(학생회)`)

### FollowBoard

게시판에 대한 Follow

(예정) StudyBoard와 AnnouncementBoard 에 대한 Follow도 지원

### Comment

khumu-comment에서 관리

### Campus

국제캠퍼스, 서울캠퍼스에 대한 정보. MVP에서는 국제캠퍼스만 다루기 때문에 서울 캠퍼스는 아직 미지원

### Organization

경희대학교의 단과대(사실 완벽히 단과대는 아니고 수강신청할 때 주로 우리가 선택하는 단위임)

### Department

경희대학교의 학과 데이터

### LectureSuite

경희대학교의 강의 (e.g. 미적분 강의)

동일한 강의를 묶어 공통적인 내용을 위주로 표현하는 강의(군)

### Lecture

경희대학교의 개별 강의 (e.g. 미적분 월 수 김OO교수님 강의, 미적분 월 수 박OO 교수님 강의, 미적분 화목 이OO 교수님 강의)

개별 강의 자체에 대한 데이터

### Notification

알림탭에 나오는 알림 내용

* `is_read` - 현재 알림을 읽었는지. GET API를 이용해 읽으면 바로 `is_read`는 true가 된다.

### ArticleNotificationSubscription

* `is_activated` - 구독이 활성화되어있는지. 
  * 댓글을 달거나 글을 생성하면 구독이 활성화된 `ArticleNotificationSubscription`이 가 생성됨.
  * 이후 Unsubscribe하면 `is_activated`는 `false`가 된다. 한 번 구독을 비활성화 시켰는데 댓글을 달 때마다 활성화되는 경우를 방지하기 위함.

### PushSubscription

KhumuUser의 push device token을 저장함. 한 KhumuUser도 여러 device token을 가질 수 있음.

## Jobs

수행해야할 몇 가지 복잡한 동작들을 Job으로 정의해서 수행하고 있다. 아직 에러 핸들링과 정확한 로그 출력이 미흡하다. 특히나 졸업생, 휴학생, 부전공, 복수전공생들에 대한 케이스는 대비가 힘듦.

_혹시라도 도와주실 학우분들 계시면 말씀해주시면 좋을 것 같습니다!!!_

* KhuAuthJob - 인포21에 인증하는 작업
* KhuLectureCollectorJob - 인포21에 인증 후 존재하는 강의 정보를 수집하는 작업
* KhuLectureSyncJob - 인포21에 인증 후 해당 계정이 수강 중인 강의와 학과의 게시판을 Follow하는 작업
* StudentQrCodeJob - 저장된 학번을 이용해 QrCode를 얻어오는 작업
* MigrateHaksaScheduleJob - 학사일정 csv 파일을 database에 migrate하는 작업.



