pipeline {
    agent any

    environment {
        IMAGE_NAME           = 'urayfaizmuhajir/flask-mysql-app'
        TAG                  = "${BUILD_NUMBER}"
        REGISTRY_CREDENTIALS = 'dockerhub-credentials'
        COMPOSE_PROJECT_NAME = 'tugas-flask-mysql'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:%TAG% .'
            }
        }

        stage('Test Image') {
            steps {
                bat 'docker run --rm %IMAGE_NAME%:%TAG% python -m py_compile app.py'
                echo 'Syntax check app.py OK'
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${REGISTRY_CREDENTIALS}",
                                                  usernameVariable: 'USER',
                                                  passwordVariable: 'PASS')]) {
                    bat 'echo %PASS%| docker login -u %USER% --password-stdin'
                    bat 'docker push %IMAGE_NAME%:%TAG%'
                    bat 'docker tag %IMAGE_NAME%:%TAG% %IMAGE_NAME%:latest'
                    bat 'docker push %IMAGE_NAME%:latest'
                }
            }
        }

        stage('Deploy App + MySQL') {
            steps {
                bat 'docker compose up -d'
                bat 'docker compose ps'
            }
        }

        stage('Verify Database Connection') {
            steps {
                powershell '''
                    for ($i = 1; $i -le 40; $i++) {
                        try {
                            $r = Invoke-WebRequest -UseBasicParsing -Uri http://localhost:5000/health -TimeoutSec 5
                            Write-Output "Health check: $($r.Content)"
                            exit 0
                        } catch {
                            Write-Output "Menunggu aplikasi & database siap... ($i/40)"
                            Start-Sleep -Seconds 3
                        }
                    }
                    Write-Error "Aplikasi gagal terhubung ke database"
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo 'Aplikasi berjalan di http://localhost:5000 dan terhubung ke MySQL'
        }
        always {
            echo 'Selesai build'
        }
    }
}
