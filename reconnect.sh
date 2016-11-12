#!/bin/bash

ping -q -c2 8.8.8.8 || sudo /etc/init.d/networking restart
