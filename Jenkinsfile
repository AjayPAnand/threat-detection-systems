pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'threat-detection-system'
        DOCKER_TAG = "${BUILD_NUMBER}"
        SONAR_PROJECT_KEY = 'threat-detection-system'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }
        
        stage('Build') {
            steps {
                echo 'Building application...'
                script {
                    // Install dependencies
                    sh 'python -m pip install --upgrade pip'
                    sh 'pip install -r requirements.txt'
                    
                    // Build Docker image
                    def image = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}", "-f docker/Dockerfile .")
                    
                    // Tag as latest
                    image.tag("latest")
                    
                    echo "Built Docker image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
            }
            post {
                success {
                    archiveArtifacts artifacts: 'requirements.txt', fingerprint: true
                }
            }
        }
        
        stage('Test') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        echo 'Running unit tests...'
                        sh '''
                            python -m pytest tests/ \
                                --junitxml=test-results.xml \
                                --cov=app \
                                --cov-report=xml \
                                --cov-report=html \
                                -v
                        '''
                    }
                }
                
                stage('Integration Tests') {
                    steps {
                        echo 'Running integration tests...'
                        sh '''
                            python -m pytest integration_tests/ \
                                --junitxml=integration-test-results.xml \
                                -v
                        '''
                    }
                }
            }
            post {
                always {
                    publishTestResults testResultsPattern: '*-test-results.xml'
                    publishCoverage adapters: [
                        coberturaAdapter('coverage.xml')
                    ], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                }
            }
        }
        
        stage('Code Quality') {
            steps {
                echo 'Running code quality analysis...'
                script {
                    withSonarQubeEnv('SonarQube') {
                        sh '''
                            sonar-scanner \
                                -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                                -Dsonar.sources=app \
                                -Dsonar.tests=tests \
                                -Dsonar.python.coverage.reportPaths=coverage.xml \
                                -Dsonar.python.xunit.reportPath=test-results.xml
                        '''
                    }
                    
                    // Wait for quality gate
                    timeout(time: 1, unit: 'HOURS') {
                        def qg = waitForQualityGate()
                        if (qg.status != 'OK') {
                            error "Pipeline aborted due to quality gate failure: ${qg.status}"
                        }
                    }
                }
            }
        }
        
        stage('Security') {
            steps {
                echo 'Running security analysis...'
                script {
                    // OWASP Dependency Check
                    sh '''
                        dependency-check \
                            --project "Threat Detection System" \
                            --scan . \
                            --format JSON \
                            --format HTML \
                            --out dependency-check-report
                    '''
                    
                    // Bandit security linter for Python
                    sh '''
                        bandit -r app/ \
                            -f json \
                            -o bandit-report.json \
                            || true
                    '''
                    
                    // Safety check for known security vulnerabilities
                    sh '''
                        safety check \
                            --json \
                            --output safety-report.json \
                            || true
                    '''
                    
                    // Trivy container scanning
                    sh '''
                        trivy image \
                            --format json \
                            --output trivy-report.json \
                                                        ${DOCKER_IMAGE}:${DOCKER_TAG} \
                            || true
                    '''
                    
                    // Parse and report security findings
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'dependency-check-report',
                        reportFiles: 'dependency-check-report.html',
                        reportName: 'OWASP Dependency Check Report'
                    ])
                    
                    // Archive security reports
                    archiveArtifacts artifacts: '*-report.json', allowEmptyArchive: true
                }
            }
            post {
                always {
                    script {
                        // Parse security reports and provide summary
                        def securitySummary = readJSON file: 'bandit-report.json'
                        echo "Security scan completed. Issues found: ${securitySummary.results?.size() ?: 0}"
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            steps {
                echo 'Deploying to staging environment...'
                script {
                    // Stop existing containers
                    sh 'docker-compose -f docker/docker-compose.staging.yml down || true'
                    
                    // Deploy to staging
                    sh '''
                        export DOCKER_TAG=${DOCKER_TAG}
                        docker-compose -f docker/docker-compose.staging.yml up -d
                    '''
                    
                    // Wait for deployment
                    sh 'sleep 30'
                    
                    // Health check
                    sh '''
                        curl -f http://localhost:5000/health || exit 1
                        echo "Staging deployment successful"
                    '''
                }
            }
            post {
                success {
                    slackSend(
                        channel: '#devops',
                        color: 'good',
                        message: ":white_check_mark: Staging deployment successful for build ${BUILD_NUMBER}"
                    )
                }
                failure {
                    slackSend(
                        channel: '#devops',
                        color: 'danger',
                        message: ":x: Staging deployment failed for build ${BUILD_NUMBER}"
                    )
                }
            }
        }
        
        stage('Smoke Tests') {
            steps {
                echo 'Running smoke tests...'
                script {
                    sh '''
                        # Test basic functionality
                        curl -f http://localhost:5000/health
                        curl -f http://localhost:5000/api/status
                        curl -f http://localhost:5000/metrics
                        
                        # Test threat analysis endpoint
                        curl -X POST \
                            -H "Content-Type: application/json" \
                            -d '{"packet_size":1024,"port":80,"protocol":"TCP","frequency":10}' \
                            http://localhost:5000/api/analyze
                    '''
                }
            }
        }
        
        stage('Release to Production') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to production...'
                script {
                    // Manual approval for production deployment
                    input message: 'Deploy to production?', ok: 'Deploy'
                    
                    // Tag for production
                    def image = docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    image.tag("prod-${DOCKER_TAG}")
                    
                    // Deploy to production
                    sh '''
                        export DOCKER_TAG=${DOCKER_TAG}
                        export SECRET_KEY=$(openssl rand -hex 32)
                        docker-compose -f docker/docker-compose.prod.yml down || true
                        docker-compose -f docker/docker-compose.prod.yml up -d
                    '''
                    
                    // Wait and verify production deployment
                    sh 'sleep 60'
                    sh 'curl -f http://localhost:80/health || exit 1'
                }
            }
            post {
                success {
                    slackSend(
                        channel: '#production',
                        color: 'good',
                        message: ":rocket: Production deployment successful for build ${BUILD_NUMBER}"
                    )
                }
            }
        }
        
        stage('Setup Monitoring') {
            steps {
                echo 'Setting up monitoring and alerting...'
                script {
                    // Configure Prometheus targets
                    sh '''
                        echo "Configuring monitoring..."
                        
                        # Update Prometheus configuration
                        cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'threat-detection-api'
    static_configs:
      - targets: ['threat-detection-api:5000']
    metrics_path: '/metrics'
    scrape_interval: 30s
    
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
EOF
                    '''
                    
                    // Create alert rules
                    sh '''
                        cat > monitoring/alert_rules.yml << EOF
groups:
- name: threat_detection_alerts
  rules:
  - alert: HighThreatDetectionRate
    expr: increase(threats_detected[5m]) > 10
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High threat detection rate"
      description: "Detected {{ $value }} threats in the last 5 minutes"
      
  - alert: ApplicationDown
    expr: up{job="threat-detection-api"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Threat Detection API is down"
      description: "The threat detection API has been down for more than 1 minute"
      
  - alert: HighResponseTime
    expr: http_request_duration_seconds{quantile="0.95"} > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value }} seconds"
EOF
                    '''
                    
                    // Restart monitoring stack
                    sh '''
                        docker-compose -f docker/docker-compose.prod.yml restart prometheus
                        echo "Monitoring setup completed"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed'
            // Clean up workspace
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
            emailext(
                subject: "Pipeline Success: ${env.JOB_NAME} - Build ${env.BUILD_NUMBER}",
                body: "The pipeline completed successfully. Build: ${env.BUILD_URL}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
        failure {
            echo 'Pipeline failed!'
            emailext(
                subject: "Pipeline FAILED: ${env.JOB_NAME} - Build ${env.BUILD_NUMBER}",
                body: "The pipeline failed. Check the build: ${env.BUILD_URL}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
        unstable {
            echo 'Pipeline unstable!'
        }
    }
}

