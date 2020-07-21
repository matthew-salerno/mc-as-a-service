#!/bin/bash
dbus-send --system --type=method_call --dest=com.salernosection.mc_as_a_service  /com/salernosection/mc_as_a_service com.salernosection.mc_as_a_service.stop_service