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
                      --exit-code 1 \
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
                      --exit-code 1 \
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
                      --exit-code 1 \
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
    }

    post {

        success {
            echo '======================================'
            echo 'DevSecOps Pipeline Completed Successfully'
            echo 'All security gates passed'
            echo 'Docker images pushed to Docker Hub'
            echo '======================================'
        }

        failure {
            echo '======================================'
            echo 'DevSecOps Pipeline FAILED'
            echo 'Check the failed stage above'
            echo '======================================'
        }

        always {
            echo "Build Number: ${BUILD_NUMBER}"
        }
    }
}
