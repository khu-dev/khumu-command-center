KHUMU_ENVIRONMENT=DEV python manage.py migrate &&
KHUMU_ENVIRONMENT=DEV python manage.py test --keepdb &&
echo "Successfully initialized dev khumu."

curl -F 'image=@./test_data/jinsu.jpeg' -F 'hashing=false' https://api.khumu.jinsu.me/api/images
curl -F 'image=@./test_data/dizzy.jpeg' -F 'hashing=false' https://api.khumu.jinsu.me/api/images
curl -F 'image=@./test_data/chihoon.jpeg' -F 'hashing=false' https://api.khumu.jinsu.me/api/images