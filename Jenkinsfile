pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Source code checked out by Jenkins'
            }
        }

        stage('Environment Check') {
            steps {
                sh '''
                    echo "Checking build environment..."

                    git --version
                    docker --version
                    trivy --version
                    sonar-scanner --version
                    semgrep --version
                '''
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

        /*
         * ============================
         * BACKEND
         * ============================
         */

        stage('Docker Build Backend') {
            steps {
                sh '''
                    echo "Building backend Docker image..."

                    docker build \
                      -t devsecops-backend:${BUILD_NUMBER} \
                      ./backend
                '''
            }
        }

        stage('Trivy Backend Scan') {
            steps {
                sh '''
                    echo "Scanning backend image with Trivy..."

                    trivy image \
                      --severity HIGH,CRITICAL \
                      --ignore-unfixed \
                      --no-progress \
                      devsecops-backend:${BUILD_NUMBER}
                '''
            }
        }

        /*
         * ============================
         * FRONTEND
         * ============================
         */

        stage('Docker Build Frontend') {
            steps {
                sh '''
                    echo "Building frontend Docker image..."

                    docker build \
                      -t devsecops-frontend:${BUILD_NUMBER} \
                      ./frontend
                '''
            }
        }

        stage('Trivy Frontend Scan') {
            steps {
                sh '''
                    echo "Scanning frontend image with Trivy..."

                    trivy image \
                      --severity HIGH,CRITICAL \
                      --ignore-unfixed \
                      --no-progress \
                      devsecops-frontend:${BUILD_NUMBER}
                '''
            }
        }

        /*
         * ============================
         * NGINX
         * ============================
         */

        stage('Docker Build Nginx') {
            steps {
                sh '''
                    echo "Building Nginx Docker image..."

                    docker build \
                      -t devsecops-nginx:${BUILD_NUMBER} \
                      ./nginx
                '''
            }
        }

        stage('Trivy Nginx Scan') {
            steps {
                sh '''
                    echo "Scanning Nginx image with Trivy..."

                    trivy image \
                      --severity HIGH,CRITICAL \
                      --ignore-unfixed \
                      --no-progress \
                      devsecops-nginx:${BUILD_NUMBER}
                '''
            }
        }

        /*
         * ============================
         * DOCKER HUB
         * ============================
         */

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
                        echo "Logging into Docker Hub..."

                        echo "$DOCKER_PASSWORD" | docker login \
                          -u "$DOCKER_USERNAME" \
                          --password-stdin

                        echo "Tagging backend image..."

                        docker tag \
                          devsecops-backend:${BUILD_NUMBER} \
                          $DOCKER_USERNAME/devsecops-backend:${BUILD_NUMBER}

                        echo "Tagging frontend image..."

                        docker tag \
                          devsecops-frontend:${BUILD_NUMBER} \
                          $DOCKER_USERNAME/devsecops-frontend:${BUILD_NUMBER}

                        echo "Tagging Nginx image..."

                        docker tag \
                          devsecops-nginx:${BUILD_NUMBER} \
                          $DOCKER_USERNAME/devsecops-nginx:${BUILD_NUMBER}

                        echo "Pushing backend image..."

                        docker push \
                          $DOCKER_USERNAME/devsecops-backend:${BUILD_NUMBER}

                        echo "Pushing frontend image..."

                        docker push \
                          $DOCKER_USERNAME/devsecops-frontend:${BUILD_NUMBER}

                        echo "Pushing Nginx image..."

                        docker push \
                          $DOCKER_USERNAME/devsecops-nginx:${BUILD_NUMBER}

                        echo "Logging out from Docker Hub..."

                        docker logout
                    '''
                }
            }
        }

        /*
         * ============================
         * DEPLOYMENT
         * ============================
         */

        stage('Deploy to Web App EC2') {
            steps {

                sshagent(credentials: ['app-server-ssh']) {

                    sh '''
                        echo "======================================"
                        echo "Deploying to web-app EC2..."
                        echo "Build Number: ${BUILD_NUMBER}"
                        echo "======================================"

                        ssh -o StrictHostKeyChecking=no ubuntu@65.0.153.17 "
                            set -e

                            echo 'Connected to web-app EC2'

                            cd /opt/devsecops-app

                            echo 'Updating image tag...'

                            sed -i 's/^IMAGE_TAG=.*/IMAGE_TAG=${BUILD_NUMBER}/' .env

                            echo 'Current IMAGE_TAG:'
                            grep '^IMAGE_TAG=' .env

                            echo 'Pulling Docker images...'

                            docker compose pull

                            echo 'Starting application...'

                            docker compose up -d

                            echo 'Checking containers...'

                            docker compose ps

                            echo 'Deployment completed successfully'
                        "
                    '''
                }
            }
        }

        /*
         * ============================
         * DEPLOYMENT HEALTH CHECK
         * ============================
         */

        stage('Deployment Health Check') {
            steps {

                sshagent(credentials: ['app-server-ssh']) {

                    sh '''
                        echo "======================================"
                        echo "Running deployment health check..."
                        echo "======================================"

                        ssh -o StrictHostKeyChecking=no ubuntu@65.0.153.17 "
                            set -e

                            cd /opt/devsecops-app

                            echo 'Container status:'

                            docker compose ps

                            echo 'Testing application on port 8081...'

                            curl -f http://localhost:8081

                            echo 'Health check PASSED'
                        "
                    '''
                }
            }
        }
    }

         stage('OWASP ZAP DAST') {
    	     steps {
        	 sh '''
            	     echo "======================================"
            	     echo "Running OWASP ZAP DAST..."
            	     echo "======================================"
			
            	     rm -f zap-report.html

           	     docker run --rm \
              	       -t \
                       -v "$WORKSPACE:/zap/wrk/:rw" \
                       zaproxy/zap-stable \
                       zap-baseline.py \
                       -t http://65.0.153.17:8081/ \
                       -r zap-report.html \
                       -I

                     echo "ZAP scan completed"

                     ls -lh zap-report.html
                 '''
                 }

             post {
                 always {
                     archiveArtifacts artifacts: 'zap-report.html',
              	                          allowEmptyArchive: true
               }
           }  
       }

    /*
     * ============================
     * POST ACTIONS
     * ============================
     */

    post {

        success {
            echo '''
======================================
DEVSECOPS PIPELINE SUCCESS
======================================

Semgrep              PASSED
SonarQube            PASSED
Quality Gate         PASSED
Backend Build        PASSED
Backend Trivy        PASSED
Frontend Build       PASSED
Frontend Trivy       PASSED
Nginx Build          PASSED
Nginx Trivy          PASSED
Docker Hub            PASSED
EC2 Deployment       PASSED
Health Check          PASSED

Application deployed successfully.
======================================
'''
        }

        failure {
            echo '''
======================================
DEVSECOPS PIPELINE FAILED
======================================

Check the failed stage above.

======================================
'''
        }

        always {
            echo "Build Number: ${BUILD_NUMBER}"
        }
    }
}
