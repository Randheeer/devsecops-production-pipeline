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
                timeout(time: 15, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        } 
	
	stage('Docker Build') {
    	    steps {
        	sh '''
            	    echo "Building backend Docker image..."

            	    docker build \
              	      -t devsecops-backend:${BUILD_NUMBER} \
              	      ./backend
        	'''
            }
	}
	
	stage('Trivy Image Scan') {
    	    steps {
        	sh '''
            	    echo "Scanning Docker image with Trivy..."

                    trivy image \
              	      --severity HIGH,CRITICAL \
                      --ignore-unfixed \
                      --no-progress \
                      devsecops-backend:${BUILD_NUMBER}
                '''
            }
	}

	stage('Docker Push') {
    steps {
        withCredentials([
            usernamePassword(
                credentialsId: 'dockerhub-credentials',
                usernameVariable: 'DOCKER_USERNAME',
                passwordVariable: 'DOCKER_PASSWORD'
            )
        ]) {
            sh '''
                echo "$DOCKER_PASSWORD" | docker login \
                  -u "$DOCKER_USERNAME" \
                  --password-stdin

                docker tag \
                  devsecops-backend:${BUILD_NUMBER} \
                  $DOCKER_USERNAME/devsecops-backend:${BUILD_NUMBER}

                docker push \
                  $DOCKER_USERNAME/devsecops-backend:${BUILD_NUMBER}

                docker logout
            '''
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
