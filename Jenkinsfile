pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Source code checked out by Jenkins'
            }
        }

        stage('Gitleaks Secret Scan') {
            steps {
                sh '''
                    echo "Running Gitleaks..."
                    gitleaks dir . --no-banner --redact
                '''
            }
        }

        stage('Environment Check') {
            steps {
                sh 'git --version'
                sh 'docker --version'
                sh 'gitleaks version'
                sh 'trivy --version'
            }
        }
    }

    post {

        success {
            echo 'Security checks passed'
        }

        failure {
            echo 'Security pipeline failed'
        }
    }
}
