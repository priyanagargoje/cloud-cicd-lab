
pipeline {
    agent {
        label 'windows-minikube'
    }

    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        DOCKER_IMAGE = 'YOUR_DOCKERHUB_USERNAME/my-flask-app'
        K8S_DEPLOYMENT = 'flask-app'
        K8S_CONTAINER = 'flask-app'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test Application') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    python --version
                    if ($LASTEXITCODE -ne 0) {
                        throw "Python is not available"
                    }

                    python -m py_compile app.py
                    if ($LASTEXITCODE -ne 0) {
                        throw "Python syntax test failed"
                    }

                    Write-Host "Application syntax test passed"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $image = "$env:DOCKER_IMAGE`:$env:BUILD_NUMBER"

                    docker build `
                        --build-arg APP_VERSION=$env:BUILD_NUMBER `
                        -t $image .

                    if ($LASTEXITCODE -ne 0) {
                        throw "Docker image build failed"
                    }
                '''
            }
        }

        stage('Push Image to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_TOKEN'
                    )
                ]) {
                    powershell '''
                        $ErrorActionPreference = "Stop"

                        $image = "$env:DOCKER_IMAGE`:$env:BUILD_NUMBER"

                        $env:DH_TOKEN |
                            docker login `
                                --username $env:DH_USER `
                                --password-stdin

                        if ($LASTEXITCODE -ne 0) {
                            throw "Docker Hub login failed"
                        }

                        docker push $image

                        if ($LASTEXITCODE -ne 0) {
                            throw "Docker Hub push failed"
                        }

                        Write-Host "Pushed image: $image"
                    '''
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $image = "$env:DOCKER_IMAGE`:$env:BUILD_NUMBER"

                    kubectl config current-context
                    if ($LASTEXITCODE -ne 0) {
                        throw "Cannot access Kubernetes context"
                    }

                    kubectl get nodes
                    if ($LASTEXITCODE -ne 0) {
                        throw "Minikube is not reachable"
                    }

                    kubectl set image `
                        "deployment/$env:K8S_DEPLOYMENT" `
                        "$env:K8S_CONTAINER=$image"

                    if ($LASTEXITCODE -ne 0) {
                        throw "Kubernetes image update failed"
                    }

                    kubectl rollout status `
                        "deployment/$env:K8S_DEPLOYMENT" `
                        --timeout=180s

                    if ($LASTEXITCODE -ne 0) {
                        throw "Kubernetes rollout failed"
                    }

                    kubectl get pods
                    Write-Host "Deployment successful: $image"
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD completed successfully.'
        }
        failure {
            echo 'CI/CD failed. Review the Jenkins console output.'
        }
    }
}
