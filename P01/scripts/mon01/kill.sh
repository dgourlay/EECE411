#! /bin/bash

PID=$(pgrep python)
kill -9 $PID
