#!/bin/bash
/usr/bin/python3 TelemetryServer.py &
/usr/bin/python3 ControlServer.py &
/usr/bin/python3 RPiCamServer.py &
wait
