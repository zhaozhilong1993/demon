#!/bin/bash

ipmitool -I lanplus -H 10.0.108.142 -U root -P PQ79ISF7ha7G chassis power status
ipmitool -I lanplus -H 10.0.108.142 -U root -P PQ79ISF7ha7G chassis bootdev pxe
ipmitool -I lanplus -H 10.0.108.142 -U root -P PQ79ISF7ha7G chassis power reset 
