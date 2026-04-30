pipeline {
    agent any

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main',
                url: 'https://github.com/VedantHirlekar/Capstone.git'
            }
        }

        stage('Verify Project') {
            steps {
                sh 'echo "Pipeline running successfully 🚀"'
                sh 'ls -la'
            }
        }

    }
}
