#!/usr/bin/bash

test_project() {
    sb2gs --overwrite --verify --id "$1" "tests/$1.sb3"
}

test_project 1290981008
