pipeline {
    agent any

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
                echo "🚀 Building Docker Images..."

                docker build -t express-app ./express_app
                docker build -t fastapi-app ./fastapi_app
                docker build -t springboot-app ./springboot_app
                docker build -t dotnet-app ./dotnet_app

                echo "✅ All images built"
                '''
            }
        }

        stage('List Images') {
            steps {
                sh 'docker images'
            }
        }

    }
}
