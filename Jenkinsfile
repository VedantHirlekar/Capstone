pipeline {
    agent any

    environment {
        AWS_REGION = "eu-north-1"
        ACCOUNT_ID = "YOUR_AWS_ACCOUNT_ID"
        ECR_URL = "767398016991.dkr.ecr.eu-north-1.amazonaws.com"
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
                docker build -t express-app ./express_app
                docker build -t fastapi-app ./fastapi_app
                docker build -t springboot-app ./springboot_app
                docker build -t dotnet-app ./dotnet_app
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
                '''
            }
        }

    }
}
