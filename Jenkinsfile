pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Source code checked out by Jenkins'
            }
        }

	stage('Semgrep SAST') {
    	    steps {
                sh '''
                    echo "Running Semgrep SAST..."

		    semgrep scan \
		      --config auto \
		      --error
        	'''
    	    }
	}

	stage('SonarQube Analysis') {
    	    steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        echo "Running SonarQube analysis..."
   
                        sonar-scanner
                    '''
                }
            }  
        }

	stage('SonarQube Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
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
