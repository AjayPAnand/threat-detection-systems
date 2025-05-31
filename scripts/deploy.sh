#!/bin/bash
set -e

ENVIRONMENT=${1:-staging}

echo "Deploying to $ENVIRONMENT environment..."

if [ "$ENVIRONMENT" = "production" ]; then
    echo "Production deployment requires manual approval"
    read -p "Are you sure you want to deploy to production? (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "Deployment cancelled"
        exit 1
    fi
    
    docker-compose -f docker/docker-compose.prod.yml down
    docker-compose -f docker/docker-compose.prod.yml up -d
    
    # Wait for services to start
    sleep 60
    
    # Health check
    curl -f http://localhost:80/health || exit 1
    echo "Production deployment successful"
    
elif [ "$ENVIRONMENT" = "staging" ]; then
    docker-compose -f docker/docker-compose.staging.yml down
    docker-compose -f docker/docker-compose.staging.yml up -d
    
    # Wait for services to start
    sleep 30
    
    # Health check
    curl -f http://localhost:5000/health || exit 1
    echo "Staging deployment successful"
    
else
    echo "Unknown environment: $ENVIRONMENT"
    echo "Usage: $0 [staging|production]"
    exit 1
fi
