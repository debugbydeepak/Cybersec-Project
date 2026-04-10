#!/bin/bash
gunicorn secureway.wsgi:application --bind 0.0.0.0:8000
