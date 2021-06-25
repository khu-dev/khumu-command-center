# KHUMU

Django REST Framework을 바탕으로한 쿠뮤의 커뮤니티 위주의 RESTful API 서버입니다. 마이크로서비스 아키텍쳐의 쿠뮤에서 특이하게 커뮤니티 도메인 외의도 인증이나 학사일정 제공 등 경희대학교 관련 몇 가지 기능들을 수행하고 있습니다.

## API Documentation

**[API Documentation](https://documenter.getpostman.com/view/13384984/TVsvfkxs)** - POSTMan의 문서화 기능을 이용해 쿠뮤의 전체 API들을 문서화하고 있습니다.

## 특징 및 동작 방식

* **커뮤니티 도메인 위주의 `RESTful API`를 제공합니다.** 

  * 일반 게시판 CRUD
  * 일반 게시글 CRUD
  * 스터디류 게시판 CRUD
  * 스터디류 게시글 CRUD
  * 회원가입, 로그인
  * 학사일정 조회

* **마이크로서비스 간에는 `메시지 큐`를 바탕으로 비동기적으로 작업하며 `느슨하게 결합`(Loosely coupled)합니다.**

  예를 들어 게시글 작성 시 `SNS`로 작성 이벤트를 Publish합니다.

  1. 게시글 작성 후 Article Model instance를 JSON으로 변환합니다. (DRF Serializer로 직렬화하는 것이 아니라 단순 직렬화)
  2. JSON 데이터를 SNS에 Publish 합니다.
  3. `SNS`에서 구독 조건과 정보를 이용해 올바른 `SQS`에게 이벤트를 전달합니다.
  4. 올바른 SQS 구독자(consumer)가 메시지를 받아 게시글 생성에 대한 이벤트를 처리합니다.
     * 예를 들어 쿠뮤의 알림 서비스인 [alimi](https://github.com/khu-dev/alimi)는 게시글 생성에 대한 이벤트를 받아 Author가 게시글에 대한 댓글 생성과 같은 추가적인 알림들을 받아볼 수 있도록 해당 게시글을 구독시킵니다.

## 개발 팁

* pip dependency
  ```bash
  $ pip freeze > requirements.txt
  # requirements.txt 작성 후 pkg-resources==0.0.0 line을 지워줘야할 수 있습니다.
  ```

* mysqlclient dependency - MySQL을 이용하기 위해서 필요한 ubuntu의 패키지들 입니다.
  * `sudo apt-get install python3-dev`
  * `sudo apt-get install libmysqlclient-dev`
    * 일반 ubuntu에서는 `libmysqlclient-dev`, python ubuntu container에서는 `default-libmysqlclient-dev`(?). 아마 후자로만 해도 될 것으로 추측합니다.
  * `pip install mysqlclient`
  * `pip install wheel`

* 다양한 환경에 따른 config 적용하기
  * `KHUMU_ENVIRONMENT` 값을 통해 이용할 환경을 설정할 수 있습니다. (`LOCAL` | `DEV`, default는 `LOCAL`)
  * `KHUMU_ENVIRONMENT` 의 값에 따라`config/local.yaml` 혹은 `config/dev.yaml` 등의 설정 파일을 통해 애플리케이션에 설정을 적용합니다. `settings.py` 에서 각종 환경에 맞는 설정을 동적으로 적용합니다.

## chrome driver을 설치하십시오

⚠️ 인포 21 인증을 비롯한 인포 21과 관련된 작업은  `Selenium`과 `chrome driver`를 사용 합니다. `chrome driver`는 project root에 위치해야 합니다.

​	이는 우리가 개발하는 "코드"가 아닌 "실행 파일"이기에 Git에는 포함하고 있지 않으니 로컬 개발 시에나 배포 시에는 `chrome driver`을 project root에 위치시켜야 함을 주의해주세요.

```shell
curl https://chromedriver.storage.googleapis.com/89.0.4389.23/chromedriver_linux64.zip -o chromedriver.zip && unzip chromedriver.zip
```

## Entities

> 작업 예정...

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

인포 21 관련 작업 혹은 종종 RESTful한 요청이 아닌 CLI로 인해 trigger되는 몇 가지 동작들을 **"Job"**이라는 개념으로 정의하고 있습니다.

(아직 에러 핸들링과 정확한 로그 출력이 미흡하고, 관리가 힘들어 마이크로서비스로 뺄 생각도 있습니다. 그리고 특히나 졸업생, 휴학생, 부전공, 복수전공생들에 대한 케이스는 대비가 힘든 상황입니다... **_혹시라도 도와주실 학우분들 계시면 말씀해주시면 좋을 것 같습니다!!!_**)

* `KhuAuthJob` - 인포21에 인증하는 작업
* `KhuLectureCollectorJob` - 인포21에 인증 후 존재하는 강의 정보를 수집하는 작업
* `KhuLectureSyncJob` - 인포21에 인증 후 해당 계정이 수강 중인 강의와 학과의 게시판을 Follow하는 작업
* `StudentQrCodeJob` - 저장된 학번을 이용해 QrCode를 얻어오는 작업
* `MigrateHaksaScheduleJob` - 학사일정 csv 파일을 database에 migrate하는 작업.



