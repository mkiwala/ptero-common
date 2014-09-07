#!/bin/bash

for f in var/log/*; do
    printf "\e[31m============= \e[1m$f\e[0m\e[31m =============\e[0m"
    echo
    cat $f
    echo
done
