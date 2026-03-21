@Library('my-shared-lib') _

pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-southeast-2'
        AWS_ACCOUNT_ID = '424322298246'
        IMAGE_NAME = 'starship-fleet'
        IMAGE_TAG = "${BUILD_NUMBER}"
        ECR_REPO = 'starship-fleet'
    }

    stages {
        stage('Checkout') {
            steps {
                checkoutCode()
            }
        }

        stage('Install Dependencies') {
            steps {
                installDependencies('pip install -r requirements.txt')
            }
        }

        stage('OWASP Scan') {
            steps {
                owaspScan(IMAGE_NAME)
            }
        }

        stage('Unit Test') {
            steps {
                unitTest('pytest')
            }
        }

        stage('SonarQube scan') {
            steps {
                sonarScan(IMAGE_NAME)
            }
        }

        stage('Quality Gate') {
            steps {
                qualityGate()
            }
        }

        stage('Build Docker Image') {
            steps {
                dockerBuild(IMAGE_NAME, IMAGE_TAG)
            }
        }

        stage('Trivy image scan') {
            steps {
                trivyScan(IMAGE_NAME, IMAGE_TAG)
            }
        }

        stage('Push Image to ECR') {
            steps {
                pushToECR(IMAGE_NAME, IMAGE_TAG, AWS_ACCOUNT_ID, AWS_REGION, ECR_REPO)
            }
        }

        stage('Deploy to Dev Environment') {
            steps {
                deployEKS(
                    "dev-cluster",
                    AWS_REGION,
                    "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:${IMAGE_TAG}",
                    "dev",
                    "starship",
                    "./helm/starship-fleet"
                )
            }
        }

        stage('Approval') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    input message: "Deploy to STAGING environment?"
                }
            }
        }

        stage('Deploy to Staging Environment') {
            steps {
                deployEKS(
                    "staging-cluster",
                    AWS_REGION,
                    "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:${IMAGE_TAG}",
                    "staging",
                    "starship",
                    "./helm/starship-fleet"
                )
            }
        }
    }
}
