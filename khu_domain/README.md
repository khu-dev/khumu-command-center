# khu_domain

캠퍼스, 단과대, 학과, 강의 등등 경희대 한정 도메인에 대한 패키지입니다.

## 도메인 정보 수집하기

`khu_domain/data.yaml`에서 캠퍼스, 단과대, 학과에 대한 초기 데이터 구축을 위한 설정을 정의합니다.

```shell
# 모든 학과에 대한 강의를 수집, 데이터 구축
$ python manage.py collect_lecture
# 정의한 학과에 한정해 학과에 대한 강의를 수집, 데이터 구축
$ python manage.py collect_lecture -o 소프트웨어융합대학 공과대학 전자정보대학
```

위의 커맨드를 통해 실제로 초기 데이터를 구축합니다.