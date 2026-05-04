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
                git branch: 'main',
                url: 'https://github.com/VedantHirlekar/Capstone.git'
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                set -e

                echo "Building express..."
                docker build -t express-app:$IMAGE_TAG ./express_app

                echo "Building fastapi..."
                docker build -t fastapi-app:$IMAGE_TAG ./fastapi_app

                echo "Building springboot..."
                docker build -t springboot-app:$IMAGE_TAG ./springboot_app

                echo "Building dotnet..."
                docker build -t dotnet-app:$IMAGE_TAG ./dotnet_app

                echo "Building nginx..."
                docker build -t nginx-gateway:$IMAGE_TAG ./nginx
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

                aws ssm send-command \
                  --region $AWS_REGION \
                  --instance-ids $INSTANCE_ID \
                  --document-name "AWS-RunShellScript" \
                  --comment "Deploy version $IMAGE_TAG" \
                  --parameters "{\\"commands\\":[
                    \\"cd /home/ssm-user/capstone-project\\",
                    \\"export IMAGE_TAG=$IMAGE_TAG\\",
                    \\"docker-compose down || true\\",
                    \\"docker-compose pull\\",
                    \\"docker-compose up -d\\"
                  ]}" \
                  --output text

                echo "Deployment sent successfully"
                """
            }
        }
    }
}
