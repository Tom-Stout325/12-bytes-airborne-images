#!/bin/bash

heroku config:set \
  EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend \
  EMAIL_HOST=smtp.office365.com \
  EMAIL_PORT=587 \
  EMAIL_USE_TLS=True \
  EMAIL_HOST_USER=tom@tom-stout.com \
  EMAIL_HOST_PASSWORD=jvqgrwknpfvftmwj \
  DEFAULT_FROM_EMAIL=tom@tom-stout.com \
  --app airborne-images-12bytes



#   Run in the terminal:
# chmod +x set_email_config.sh
# ./set_email_config.sh


heroku config:set \
  DEBUG=False \
  USE_S3=False \
  --app airborne-images-12bytes
