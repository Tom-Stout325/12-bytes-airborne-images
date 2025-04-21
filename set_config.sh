#!/bin/bash

# Set Heroku config vars for 12Bytes project
heroku config:set \
  DEBUG=False \
  DJANGO_SECRET_KEY='your-production-secret-key' \
  EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend \
  EMAIL_HOST=smtp.office365.com \
  EMAIL_PORT=587 \
  EMAIL_USE_TLS=True \
  EMAIL_HOST_USER=tom@tom-stout.com \
  EMAIL_HOST_PASSWORD=jvqgrwknpfvftmwj \
  DEFAULT_FROM_EMAIL=tom@tom-stout.com \
  USE_S3=False \
  --app airborne-images-12bytes

# Uncomment and run this block if using S3
# heroku config:set \
#   AWS_ACCESS_KEY_ID=your-access-key-id \
#   AWS_SECRET_ACCESS_KEY=your-secret-access-key \
#   AWS_STORAGE_BUCKET_NAME=your-bucket-name \
#   AWS_S3_REGION_NAME=us-east-1 \
#   --app airborne-images-12bytes