#!/usr/bin/env bash

ps aux | grep "[s]sh -fN -D localhost:1081 receval.tunnel"
if [ $? -eq 0 ]; then
  echo "SSH tunnel is running."
else
  echo "SSH tunnel is not running. Starting new tunnel..."
  ssh -fN -D localhost:1081 receval.tunnel
fi
