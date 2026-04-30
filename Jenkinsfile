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

    }
}
