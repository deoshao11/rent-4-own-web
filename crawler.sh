#!/bin/bash

echo "--------------------------------"
echo "Starting Crawling Service"
echo "--------------------------------"

for zipcode in 07101 07104 07107 07114 07188 07193 07199 07102 07105 07108 07175 07191 07195 07201 07103 07106 07112 07184 07192 07198
do
  python3 zillow.py $zipcode newest
done
