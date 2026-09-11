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

	stage('Semgrep SAST') {
    	    steps {
                sh '''
                    echo "Running Semgrep SAST..."
                    semgrep scan --config auto .
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
