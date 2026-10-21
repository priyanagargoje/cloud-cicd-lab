
pipeline {
    agent any

    environment {
        AWS_REGION     = 'ap-south-1'
        AWS_ACCOUNT_ID  = '164607045936'
        ECR_REPOSITORY  = 'image-regi'
        IMAGE_NAME      = 'cloud-image'
        ECR_REGISTRY    = '164607045936.dkr.ecr.ap-south-1.amazonaws.com'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and Test') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    python --version
                    if ($LASTEXITCODE -ne 0) {
                        throw "Python is not available"
                    }

                    python -m py_compile app.py
                    if ($LASTEXITCODE -ne 0) {
                        throw "Python syntax check failed"
                    }

                    Write-Host "Build and test successful"
                '''
            }
        }

        stage('Docker Build') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $tag = "$env:BUILD_NUMBER"
                    $image = "$env:IMAGE_NAME`:$tag"

                    docker build -t $image .

                    if ($LASTEXITCODE -ne 0) {
                        throw "Docker build failed"
                    }
                '''
            }
        }

        stage('ECR Login') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $password = aws ecr get-login-password `
                        --region $env:AWS_REGION

                    if ($LASTEXITCODE -ne 0 -or !$password) {
                        throw "Unable to obtain ECR login token. Check AWS credentials."
                    }

                    $password | docker login `
                        --username AWS `
                        --password-stdin $env:ECR_REGISTRY

                    if ($LASTEXITCODE -ne 0) {
                        throw "ECR login failed"
                    }
                '''
            }
        }

        stage('Docker Tag') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $tag = "$env:BUILD_NUMBER"
                    $sourceImage = "$env:IMAGE_NAME`:$tag"
                    $targetImage = "$env:ECR_REGISTRY/$env:ECR_REPOSITORY`:$tag"

                    docker tag $sourceImage $targetImage

                    if ($LASTEXITCODE -ne 0) {
                        throw "Docker tag failed"
                    }
                '''
            }
        }

        stage('Push to ECR') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $tag = "$env:BUILD_NUMBER"
                    $image = "$env:ECR_REGISTRY/$env:ECR_REPOSITORY`:$tag"

                    docker push $image

                    if ($LASTEXITCODE -ne 0) {
                        throw "Docker push failed"
                    }

                    Write-Host "Successfully pushed: $image"
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
            echo 'Image pushed to Amazon ECR.'
        }

        failure {
            echo 'Pipeline failed! Check Console Output for the failing stage.'
        }
    }
}
