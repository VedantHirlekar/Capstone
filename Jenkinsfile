pipeline {
    agent any
    
    // Add parameters for rollback functionality
    parameters {
        choice(
            name: 'ACTION',
            choices: ['deploy', 'rollback'],
            description: 'Select action to perform'
        )
        choice(
            name: 'SERVICE',
            choices: ['all', 'express-app', 'fastapi-app', 'springboot-app', 'dotnet-app', 'nginx-gateway'],
            description: 'Select service to rollback (only for rollback action)'
        )
        string(
            name: 'ROLLBACK_TAG',
            defaultValue: '',
            description: 'Tag version to rollback to (e.g., 123) - only for rollback action'
        )
    }

    environment {
        AWS_REGION = "eu-north-1"
        ECR_URL = "767398016991.dkr.ecr.eu-north-1.amazonaws.com"
        ACCOUNT_ID = "767398016991"
        INSTANCE_ID = "i-0c4b303e260d39a2b"
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout Code') {
            when { expression { params.ACTION == 'deploy' } }
            steps {
                git branch: 'main',
                url: 'https://github.com/VedantHirlekar/Capstone.git'
            }
        }

        stage('Build Docker Images') {
            when { expression { params.ACTION == 'deploy' } }
            steps {
                sh '''
                set -e

                echo "Building express..."
                docker build --no-cache -t express-app:$IMAGE_TAG ./express_app

                echo "Building fastapi..."
                docker build --no-cache -t fastapi-app:$IMAGE_TAG ./fastapi_app

                echo "Building springboot..."
                docker build --no-cache -t springboot-app:$IMAGE_TAG ./springboot_app

                echo "Building dotnet..."
                docker build --no-cache -t dotnet-app:$IMAGE_TAG ./dotnet_app

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
            when { expression { params.ACTION == 'deploy' } }
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
            when { expression { params.ACTION == 'deploy' } }
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
            when { expression { params.ACTION == 'deploy' } }
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

        stage('Rollback Service') {
            when { expression { params.ACTION == 'rollback' && params.ROLLBACK_TAG != '' } }
            steps {
                // Validate rollback tag is provided
                script {
                    if (params.ROLLBACK_TAG == '') {
                        error "ROLLBACK_TAG parameter is required for rollback action"
                    }
                }
                
                sh """
                set -e
                
                echo "Starting rollback to version: ${params.ROLLBACK_TAG}"
                echo "Service(s) to rollback: ${params.SERVICE}"
                
                # Login to ECR first
                aws ecr get-login-password --region ${AWS_REGION} | \
                docker login --username AWS --password-stdin ${ECR_URL}
                
                # Rollback based on service selection
                if [ "${params.SERVICE}" = "all" ]; then
                    echo "Rolling back all services..."
                    
                    # Pull and tag each service with the rollback version
                    for service in express-app fastapi-app springboot-app dotnet-app nginx-gateway; do
                        echo "Rolling back \$service to ${params.ROLLBACK_TAG}"
                        docker pull ${ECR_URL}/\$service:${params.ROLLBACK_TAG} || true
                        docker tag ${ECR_URL}/\$service:${params.ROLLBACK_TAG} ${ECR_URL}/\$service:latest || true
                        docker push ${ECR_URL}/\$service:latest || true
                    done
                else
                    echo "Rolling back ${params.SERVICE} to ${params.ROLLBACK_TAG}"
                    docker pull ${ECR_URL}/${params.SERVICE}:${params.ROLLBACK_TAG}
                    docker tag ${ECR_URL}/${params.SERVICE}:${params.ROLLBACK_TAG} ${ECR_URL}/${params.SERVICE}:latest
                    docker push ${ECR_URL}/${params.SERVICE}:latest
                fi
                
                # Trigger deployment on EC2
                echo "Triggering deployment on EC2 instance..."
                aws ssm send-command \
                  --region ${AWS_REGION} \
                  --instance-ids ${INSTANCE_ID} \
                  --document-name "AWS-RunShellScript" \
                  --comment "Rollback to version ${params.ROLLBACK_TAG}" \
                  --parameters '{"commands":[
                    "cd /home/ssm-user/capstone-project",
                    "echo "Rolling back to version ${params.ROLLBACK_TAG}"",
                    "docker-compose down || true",
                    "docker-compose pull",
                    "docker-compose up -d",
                    "sleep 10",
                    "docker-compose restart nginx",
                    "echo "Rollback to ${params.ROLLBACK_TAG} completed successfully""
                  ]}' \
                  --output text
                
                echo "Rollback command sent successfully"
                """
            }
        }
    }
    
    // Optional: Add post-rollback verification
    post {
        failure {
            script {
                if (params.ACTION == 'rollback') {
                    echo "Rollback failed. Please check the logs and try again."
                    // Optionally notify team about rollback failure
                } else if (params.ACTION == 'deploy') {
                    echo "Deployment failed. Consider using rollback action."
                }
            }
        }
        success {
            script {
                if (params.ACTION == 'rollback') {
                    echo "Rollback completed successfully to version ${params.ROLLBACK_TAG}"
                } else if (params.ACTION == 'deploy') {
                    echo "Deployment completed successfully with version ${IMAGE_TAG}"
                }
            }
        }
    }
}
