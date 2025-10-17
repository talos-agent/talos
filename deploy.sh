#!/bin/bash

# 1. Clone the repository
git clone https://github.com/your-org/uniaolives
cd uniaolives

# 2. Start the UniaoLives platform
docker compose -f docker-compose.uniaolives.yml up -d

# 3. Wait for the platform to start
sleep 60

# 4. Get the onion hostname
onion_hostname=$(docker exec tor cat /var/lib/tor/uniaolives.onion/hostname)
echo "UniaoLives onion hostname: $onion_hostname"