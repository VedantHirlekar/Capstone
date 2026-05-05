pipeline {
    agent any

    environment {
        AWS_REGION = "eu-north-1"
        ECR_URL = "767398016991.dkr.ecr.eu-north-1.amazonaws.com"
        INSTANCE_ID = "i-0c4b303e260d39a2b"
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout Code') {
            steps {
                cleanWs()  // Clean workspace to ensure fresh code
                git branch: 'main',
                    url: 'https://github.com/VedantHirlekar/Capstone.git'
                
                // Verify health endpoint exists in code
                sh '''
                echo "Verifying health endpoints in code..."
                grep -A5 "app.get.*/health" express_app/server.js || echo "WARNING: Health endpoint not found in express"
                grep -A5 "@app.get.*/health" fastapi_app/main.py || echo "WARNING: Health endpoint not found in fastapi"
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                set -e

                echo "Building express with no cache..."
                docker build --no-cache -t express-app:$IMAGE_TAG ./express_app

                echo "Building fastapi with no cache..."
                docker build --no-cache -t fastapi-app:$IMAGE_TAG ./fastapi_app

                echo "Building springboot..."
                docker build --no-cache -t springboot-app:$IMAGE_TAG ./springboot_app

                echo "Building dotnet..."
                docker build --no-cache -t dotnet-app:$IMAGE_TAG ./dotnet_app

                echo "Building nginx..."
                docker build --no-cache -t nginx-gateway:$IMAGE_TAG ./nginx
                '''
            }
        }

        stage('Login to ECR') {
            steps {
                sh '''
                aws ecr get-login-password --region $AWS_REGION | \
                docker login --username AWS --password-stdin $ECR_URL
                '''
            }
        }

        stage('Tag Images') {
            steps {
                sh '''
                # version tags
                docker tag express-app:$IMAGE_TAG $ECR_URL/express-app:$IMAGE_TAG
                docker tag fastapi-app:$IMAGE_TAG $ECR_URL/fastapi-app:$IMAGE_TAG
                docker tag springboot-app:$IMAGE_TAG $ECR_URL/springboot-app:$IMAGE_TAG
                docker tag dotnet-app:$IMAGE_TAG $ECR_URL/dotnet-app:$IMAGE_TAG
                docker tag nginx-gateway:$IMAGE_TAG $ECR_URL/nginx-gateway:$IMAGE_TAG

                # latest tags
                docker tag express-app:$IMAGE_TAG $ECR_URL/express-app:latest
                docker tag fastapi-app:$IMAGE_TAG $ECR_URL/fastapi-app:latest
                docker tag springboot-app:$IMAGE_TAG $ECR_URL/springboot-app:latest
                docker tag dotnet-app:$IMAGE_TAG $ECR_URL/dotnet-app:latest
                docker tag nginx-gateway:$IMAGE_TAG $ECR_URL/nginx-gateway:latest
                '''
            }
        }

        stage('Push to ECR') {
            steps {
                sh '''
                # version push
                docker push $ECR_URL/express-app:$IMAGE_TAG
                docker push $ECR_URL/fastapi-app:$IMAGE_TAG
                docker push $ECR_URL/springboot-app:$IMAGE_TAG
                docker push $ECR_URL/dotnet-app:$IMAGE_TAG
                docker push $ECR_URL/nginx-gateway:$IMAGE_TAG

                # latest push
                docker push $ECR_URL/express-app:latest
                docker push $ECR_URL/fastapi-app:latest
                docker push $ECR_URL/springboot-app:latest
                docker push $ECR_URL/dotnet-app:latest
                docker push $ECR_URL/nginx-gateway:latest
                '''
            }
        }

        stage('Deploy on EC2 via SSM') {
            steps {
                sh """
                set -e

                echo "Deploying version: $IMAGE_TAG"

                # Create deployment script
                cat > /tmp/deploy.sh << 'SCRIPT'
#!/bin/bash
set -e

cd /home/ssm-user/capstone-project

echo "=== Stopping containers ==="
docker-compose down

echo "=== Removing old images to force fresh pull ==="
docker rmi $ECR_URL/express-app:latest || true
docker rmi $ECR_URL/fastapi-app:latest || true
docker rmi $ECR_URL/springboot-app:latest || true
docker rmi $ECR_URL/dotnet-app:latest || true
docker rmi $ECR_URL/nginx-gateway:latest || true

echo "=== Pulling latest images ==="
docker-compose pull

echo "=== Starting containers ==="
docker-compose up -d

echo "=== Waiting for containers to be ready ==="
sleep 10

echo "=== Testing health endpoints ==="
curl -f http://localhost:3001/health || echo "Express health endpoint not ready"
curl -f http://localhost:8002/health || echo "FastAPI health endpoint not ready"

echo "=== Container status ==="
docker ps --format "table {{.Names}}\\t{{.Status}}"

echo "=== Deployment complete ==="
SCRIPT

                # Make script executable
                chmod +x /tmp/deploy.sh

                # Send and execute script via SSM
                aws ssm send-command \
                  --region $AWS_REGION \
                  --instance-ids $INSTANCE_ID \
                  --document-name "AWS-RunShellScript" \
                  --comment "Deploy version $IMAGE_TAG" \
                  --parameters "{\\"commands\\":[\\"bash /tmp/deploy.sh\\"]}" \
                  --output text

                echo "Deployment sent successfully"
                """
            }
        }

        stage('Verify Deployment') {
            steps {
                sh """
                echo "Waiting for deployment to complete..."
                sleep 15
                
                # Run verification commands
                aws ssm send-command \
                  --region $AWS_REGION \
                  --instance-ids $INSTANCE_ID \
                  --document-name "AWS-RunShellScript" \
                  --comment "Verify deployment" \
                  --parameters "{\\"commands\\":[
                    \\"cd /home/ssm-user/capstone-project\\",
                    \\"echo '=== Health Check Results ==='\\",
                    \\"curl -s http://localhost:3001/health | python3 -m json.tool || echo 'Express health check failed'\\",
                    \\"echo ''\\",
                    \\"curl -s http://localhost:8002/health | python3 -m json.tool || echo 'FastAPI health check failed'\\"
                  ]}" \
                  --output text
                """
            }
        }
    }
    
    post {
        success {
            echo "Deployment successful! Version: ${env.IMAGE_TAG}"
        }
        failure {
            echo "Deployment failed! Check Jenkins logs for details."
        }
    }
}
