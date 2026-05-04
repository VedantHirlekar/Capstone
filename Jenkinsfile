pipeline {
    agent any

    environment {
        AWS_REGION = "eu-north-1"
        ECR_URL = "767398016991.dkr.ecr.eu-north-1.amazonaws.com"
        INSTANCE_ID = "i-0c4b303e260d39a2b"
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
                docker build -t express-app ./express_app

                echo "Building fastapi..."
                docker build -t fastapi-app ./fastapi_app

                echo "Building springboot..."
                docker build -t springboot-app ./springboot_app

                echo "Building dotnet..."
                docker build -t dotnet-app ./dotnet_app

                echo "Building nginx..."
                docker build -t nginx-gateway ./nginx
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
                docker tag express-app $ECR_URL/express-app:latest
                docker tag fastapi-app $ECR_URL/fastapi-app:latest
                docker tag springboot-app $ECR_URL/springboot-app:latest
                docker tag dotnet-app $ECR_URL/dotnet-app:latest
                docker tag nginx-gateway $ECR_URL/nginx-gateway:latest
                '''
            }
        }

        stage('Push to ECR') {
            steps {
                sh '''
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

                echo "Deploying to EC2 via SSM..."

                aws ssm send-command \
                  --region $AWS_REGION \
                  --instance-ids $INSTANCE_ID \
                  --document-name "AWS-RunShellScript" \
                  --comment "Deploy Docker Containers" \
                  --parameters "{\\"commands\\":[
                    \\"cd /home/ssm-user/capstone-project\\",
                    \\"docker-compose down || true\\",
                    \\"docker-compose pull\\",
                    \\"docker-compose up -d\\"
                  ]}" \
                  --output text

                echo "SSM command sent successfully"
                """
            }
        }
    }
}
