pipeline {

    agent any

    environment {
        DOCKERHUB_USER = 'randheeer'

        BACKEND_IMAGE  = 'randheeer/devsecops-backend'
        FRONTEND_IMAGE = 'randheeer/devsecops-frontend'
        NGINX_IMAGE    = 'randheeer/devsecops-nginx'

        SONARQUBE_ENV = 'SonarQube'
    }

    stages {

        // =========================================================
        // 1. CHECKOUT
        // =========================================================

        stage('Checkout') {
            steps {
                echo '======================================'
                echo 'Checking out source code...'
                echo '======================================'

                checkout scm
            }
        }


        // =========================================================
        // 2. ENVIRONMENT CHECK
        // =========================================================

        stage('Environment Check') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Environment Check"
                    echo "======================================"

                    echo "Java:"
                    java -version

                    echo ""
                    echo "Docker:"
                    docker --version

                    echo ""
                    echo "Docker Compose:"
                    docker compose version

                    echo ""
                    echo "Semgrep:"
                    semgrep --version

                    echo ""
                    echo "SonarScanner:"
                    sonar-scanner --version

                    echo ""
                    echo "Trivy:"
                    trivy --version

                    echo ""
                    echo "Jenkins workspace:"
                    pwd
                '''
            }
        }


        // =========================================================
        // 3. SEMGREP SAST
        // =========================================================

        stage('Semgrep SAST') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Running Semgrep SAST..."
                    echo "======================================"

                    semgrep scan \
                      --config auto \
                      --error
                '''
            }
        }


        // =========================================================
        // 4. SONARQUBE ANALYSIS
        // =========================================================

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        echo "======================================"
                        echo "Running SonarQube Analysis..."
                        echo "======================================"

                        sonar-scanner
                    '''
                }
            }
        }


        // =========================================================
        // 5. SONARQUBE QUALITY GATE
        // =========================================================

        stage('SonarQube Quality Gate') {
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }


        // =========================================================
        // 6. BACKEND DOCKER BUILD
        // =========================================================

        stage('Build Backend Image') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Building Backend Docker Image"
                    echo "======================================"

                    docker build \
                      -t ${BACKEND_IMAGE}:${BUILD_NUMBER} \
                      ./backend

                    echo ""
                    echo "Backend image created:"
                    docker images ${BACKEND_IMAGE}
                '''
            }
        }


        // =========================================================
        // 7. BACKEND TRIVY
        // =========================================================

        stage('Trivy Backend Scan') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Scanning Backend Image with Trivy"
                    echo "======================================"

                    trivy image \
                      --severity HIGH,CRITICAL \
                      --ignore-unfixed \
                      --no-progress \
                      ${BACKEND_IMAGE}:${BUILD_NUMBER}
                '''
            }
        }


        // =========================================================
        // 8. FRONTEND DOCKER BUILD
        // =========================================================

        stage('Build Frontend Image') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Building Frontend Docker Image"
                    echo "======================================"

                    docker build \
                      -t ${FRONTEND_IMAGE}:${BUILD_NUMBER} \
                      ./frontend

                    echo ""
                    echo "Frontend image created:"
                    docker images ${FRONTEND_IMAGE}
                '''
            }
        }


        // =========================================================
        // 9. FRONTEND TRIVY
        // =========================================================

        stage('Trivy Frontend Scan') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Scanning Frontend Image with Trivy"
                    echo "======================================"

                    trivy image \
                      --severity HIGH,CRITICAL \
                      --ignore-unfixed \
                      --no-progress \
                      ${FRONTEND_IMAGE}:${BUILD_NUMBER}
                '''
            }
        }


        // =========================================================
        // 10. NGINX DOCKER BUILD
        // =========================================================

        stage('Build Nginx Image') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Building Nginx Docker Image"
                    echo "======================================"

                    docker build \
                      -t ${NGINX_IMAGE}:${BUILD_NUMBER} \
                      ./nginx

                    echo ""
                    echo "Nginx image created:"
                    docker images ${NGINX_IMAGE}
                '''
            }
        }


        // =========================================================
        // 11. NGINX TRIVY
        // =========================================================

        stage('Trivy Nginx Scan') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Scanning Nginx Image with Trivy"
                    echo "======================================"

                    trivy image \
                      --severity HIGH,CRITICAL \
                      --ignore-unfixed \
                      --no-progress \
                      ${NGINX_IMAGE}:${BUILD_NUMBER}
                '''
            }
        }


        // =========================================================
        // 12. DOCKER HUB LOGIN + PUSH
        // =========================================================

        stage('Push Images to Docker Hub') {
            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {

                    sh '''
                        echo "======================================"
                        echo "Logging into Docker Hub"
                        echo "======================================"

                        echo "$DOCKER_PASSWORD" | docker login \
                          -u "$DOCKER_USERNAME" \
                          --password-stdin

                        echo ""
                        echo "Pushing Backend..."
                        docker push ${BACKEND_IMAGE}:${BUILD_NUMBER}

                        echo ""
                        echo "Pushing Frontend..."
                        docker push ${FRONTEND_IMAGE}:${BUILD_NUMBER}

                        echo ""
                        echo "Pushing Nginx..."
                        docker push ${NGINX_IMAGE}:${BUILD_NUMBER}

                        echo ""
                        echo "Docker images pushed successfully."

                        docker logout
                    '''
                }
            }
        }


        // =========================================================
        // 13. DEPLOY TO AWS EC2
        // =========================================================

        stage('Deploy to Web App EC2') {
            steps {

                sshagent(credentials: ['app-server-ssh']) {

                    sh '''
                        echo "======================================"
                        echo "Deploying to web-app EC2..."
                        echo "======================================"

                        echo "Build Number: ${BUILD_NUMBER}"

                        ssh \
                          -o StrictHostKeyChecking=no \
                          -o BatchMode=yes \
                          ubuntu@65.0.153.17 "
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


        // =========================================================
        // 14. DEPLOYMENT HEALTH CHECK
        // =========================================================

        stage('Deployment Health Check') {
            steps {

                sshagent(credentials: ['app-server-ssh']) {

                    sh '''
                        echo "======================================"
                        echo "Running deployment health check..."
                        echo "======================================"

                        ssh \
                          -o StrictHostKeyChecking=no \
                          -o BatchMode=yes \
                          ubuntu@65.0.153.17 "
                            set -e

                            cd /opt/devsecops-app

                            echo 'Container status:'

                            docker compose ps

                            echo ''
                            echo 'Testing application on port 8081...'

                            curl -f http://localhost:8081

                            echo ''
                            echo 'Health check PASSED'
                        "
                    '''
                }
            }
        }


        // =========================================================
        // 15. OWASP ZAP DAST
        // =========================================================

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

                    echo ""
                    echo "======================================"
                    echo "ZAP Scan Completed"
                    echo "======================================"

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

    }


    // =============================================================
    // PIPELINE POST ACTIONS
    // =============================================================

    post {

        success {
            echo "======================================"
            echo "CI/CD PIPELINE SUCCESSFUL"
            echo "Build Number: ${BUILD_NUMBER}"
            echo "======================================"
        }

        failure {
            echo "======================================"
            echo "CI/CD PIPELINE FAILED"
            echo "Build Number: ${BUILD_NUMBER}"
            echo "======================================"
        }

        always {
            echo "======================================"
            echo "Pipeline finished with status:"
            echo "${currentBuild.currentResult}"
            echo "======================================"
        }
    }
}
