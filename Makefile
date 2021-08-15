init:
	KHUMU_ENVIRONMENT=DEV python manage.py makemigrations && \
	KHUMU_ENVIRONMENT=DEV python manage.py migrate && \
	KHUMU_ENVIRONMENT=DEV python manage.py initialize # khumu/management의 custom command
	# 초기 데이터에 필요한 이미지 업로드
	curl -F 'image=@./test_data/jinsu.jpeg' -F 'hashing=false' https://api.dev.khumu.me/api/images
	curl -F 'image=@./test_data/dizzy.jpeg' -F 'hashing=false' https://api.dev.khumu.me/api/images
	curl -F 'image=@./test_data/chihoon.jpeg' -F 'hashing=false' https://api.dev.khumu.me/api/images