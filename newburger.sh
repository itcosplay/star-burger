#!/bin/bash
set -e
cd /opt/projects/star-burger/
source venv/bin/activate
git fetch
git pull
python3 -m pip install --upgrade pip
pip install -r requirements.txt
echo 'node version:'
node --version
echo 'npm version:'
npm --version
npm install --dev
sudo npm install -g parcel@2.0.0-beta.2
echo 'parcel version:'
parcel --version
parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
rm -r static
python manage.py collectstatic
python manage.py migrate
systemctl restart star-burger.service
echo 'star-burger was updated successfully!'
python deploynotify.py
