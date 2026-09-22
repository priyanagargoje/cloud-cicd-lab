pipeline {
    agent any
    stages {
        stage('Clone') {
            steps {
                git 'https://github.com/USERNAME/cloud-cicd-lab.git'
            }
        }
        stage('Build') {
            steps {
                sh 'docker build -t cloud-app .'
            }
        }
        stage('Deploy') {
            steps {
                sh '''
                docker stop cloud-app || true
                docker rm cloud-app || true
                docker run -d --name cloud-app -p 5000:5000 cloud-app
                '''
            }
        }
    }
}

