#!/bin/sh
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

export FLASK_APP=src/app.py
coverage run -m pytest && coverage report