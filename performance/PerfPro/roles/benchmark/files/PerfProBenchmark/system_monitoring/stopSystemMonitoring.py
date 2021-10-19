#!/usr/bin/env python3
import os
if os.path.isfile("pidfile"):
    os.remove("pidfile")
else:
    print("No systemstats are running! Nothing to stop. Exiting")
