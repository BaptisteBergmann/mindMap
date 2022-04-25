#!/bin/sh
cd ../
export FLASK_APP=src/app.py
coverage run -m pytest && coverage report