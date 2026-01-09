#!/bin/bash

# AWS Deployment Script for RCA Chatbot
# This script builds and deploys the application to AWS ECS

set -e

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
ECR_REPO=${ECR_REPO:-rca-chatbot}
AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID:-YOUR_ACCOUNT_ID}

echo "🚀 Starting deployment to AWS..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Login to ECR
echo "📦 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Create ECR repository if it doesn't exist
echo "📦 Creating ECR repository if needed..."
aws ecr describe-repositories --repository-names $ECR_REPO --region $AWS_REGION || \
    aws ecr create-repository --repository-name $ECR_REPO --region $AWS_REGION

ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO"

# Build and push backend
echo "🔨 Building backend image..."
cd backend
docker build -t $ECR_URI-backend:latest .
docker tag $ECR_URI-backend:latest $ECR_URI-backend:$(date +%Y%m%d-%H%M%S)
echo "📤 Pushing backend image..."
docker push $ECR_URI-backend:latest
docker push $ECR_URI-backend:$(date +%Y%m%d-%H%M%S)
cd ..

# Build and push frontend
echo "🔨 Building frontend image..."
cd frontend
docker build -t $ECR_URI-frontend:latest .
docker tag $ECR_URI-frontend:latest $ECR_URI-frontend:$(date +%Y%m%d-%H%M%S)
echo "📤 Pushing frontend image..."
docker push $ECR_URI-frontend:latest
docker push $ECR_URI-frontend:$(date +%Y%m%d-%H%M%S)
cd ..

# Update ECS service (if exists)
echo "🔄 Updating ECS service..."
if aws ecs describe-services --cluster rca-chatbot-cluster --services rca-chatbot-service --region $AWS_REGION &> /dev/null; then
    aws ecs update-service \
        --cluster rca-chatbot-cluster \
        --service rca-chatbot-service \
        --force-new-deployment \
        --region $AWS_REGION
    echo "✅ Service update initiated"
else
    echo "⚠️  ECS service not found. Please create it manually or use Terraform/CloudFormation."
fi

echo "✅ Deployment complete!"


