#!/bin/sh
# marek kuczynski
# @marekq
# www.marek.rocks
# coding: utf-8

# set cli colors and library directory
RED='\033[0;31m'
NC='\033[0m'
dirn='./lambda/libs'


# download python package dependancies
echo -e "\n${RED}@@@ downloading packages with pip3${NC}\n"
rm -rf $dirn && mkdir $dirn
pip3 install -r ./lambda/requirements.txt -t ./lambda/libs -U


# run sam validate to check the sam template
echo -e "\n${RED}@@@ running sam validate locally to test the sam template${NC}\n"
sam validate


# run sam local invoke to check if the function runs correctly
echo -e "\n${RED}@@@ running sam local invoke locally to test function${NC}\n"
sam local invoke


# check if samconfig.toml file is present and deploy
if [ ! -f samconfig.toml ]; then
    echo "no samconfig.toml found, starting guided deploy"
    sam deploy -g
else
    echo "samconfig.toml found, proceeding to deploy"
    sam deploy
fi
