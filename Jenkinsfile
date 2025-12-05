pipeline {
    agent any
    
    tools {
        python3 'Python3'
    }
    
    environment {
        // 项目路径
        PROJECT_DIR = "${WORKSPACE}"
        
        // Python虚拟环境
        VENV_PATH = "${WORKSPACE}/venv"
        
        // 报告路径
        REPORTS_DIR = "${WORKSPACE}/reports"
        MODELS_DIR = "${WORKSPACE}/models"
        DATA_DIR = "${WORKSPACE}/data"
    }
    
    stages {
        stage('初始化') {
            steps {
                script {
                    echo '=== 初始化环境 ==='
                    
                    // 检查工作空间
                    sh """
                        echo "工作空间: ${WORKSPACE}"
                        echo "项目目录: ${PROJECT_DIR}"
                        ls -la
                    """
                }
            }
        }
        
        stage('检出代码') {
            steps {
                checkout scm
                
                script {
                    echo '代码检出完成'
                    sh "ls -la ${PROJECT_DIR}"
                }
            }
        }
        
        stage('安装依赖') {
            steps {
                script {
                    echo '=== 安装Python依赖 ==='
                    
                    sh """
                        cd ${PROJECT_DIR}
                        
                        # 创建虚拟环境
                        python3 -m venv ${VENV_PATH} || echo "venv已存在"
                        
                        # 激活虚拟环境并安装依赖
                        . ${VENV_PATH}/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        
                        # 显示已安装的包
                        pip list
                    """
                }
            }
        }
        
        stage('数据收集') {
            steps {
                script {
                    echo '=== 收集数据 ==='
                    
                    sh """
                        cd ${PROJECT_DIR}
                        . ${VENV_PATH}/bin/activate
                        
                        # 运行数据收集脚本
                        python3 scripts/data_collection.py
                        
                        # 检查数据是否下载成功
                        echo "数据文件:"
                        ls -la data/raw/
                    """
                }
            }
            
            post {
                success {
                    echo '数据收集成功'
                    archiveArtifacts artifacts: 'data/raw/*.csv', fingerprint: true
                }
                failure {
                    echo '数据收集失败'
                }
            }
        }
        
        stage('数据预处理') {
            steps {
                script {
                    echo '=== 预处理数据 ==='
                    
                    sh """
                        cd ${PROJECT_DIR}
                        . ${VENV_PATH}/bin/activate
                        
                        # 运行数据预处理脚本
                        python3 scripts/data_preprocessing.py
                        
                        # 检查处理后的数据
                        echo "处理后的数据文件:"
                        ls -la data/processed/
                    """
                }
            }
            
            post {
                success {
                    echo '数据预处理成功'
                    archiveArtifacts artifacts: 'data/processed/*.npy', fingerprint: true
                    archiveArtifacts artifacts: 'data/processed/*.txt', fingerprint: true
                }
            }
        }
        
        stage('训练模型') {
            steps {
                script {
                    echo '=== 训练机器学习模型 ==='
                    
                    sh """
                        cd ${PROJECT_DIR}
                        . ${VENV_PATH}/bin/activate
                        
                        # 训练模型
                        python3 scripts/train_model.py
                        
                        # 检查模型文件
                        echo "模型文件:"
                        ls -la models/
                    """
                }
            }
            
            post {
                success {
                    echo '模型训练成功'
                    archiveArtifacts artifacts: 'models/*.joblib', fingerprint: true
                    archiveArtifacts artifacts: 'models/*.pkl', fingerprint: true
                    archiveArtifacts artifacts: 'models/*.json', fingerprint: true
                }
            }
        }
        
        stage('评估模型') {
            steps {
                script {
                    echo '=== 评估模型性能 ==='
                    
                    sh """
                        cd ${PROJECT_DIR}
                        . ${VENV_PATH}/bin/activate
                        
                        # 评估模型
                        python3 scripts/evaluate_model.py
                        
                        # 检查报告文件
                        echo "评估报告:"
                        ls -la reports/
                    """
                }
            }
            
            post {
                success {
                    echo '模型评估成功'
                    
                    // 发布HTML报告
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports',
                        reportFiles: 'evaluation_report.html',
                        reportName: 'ML模型评估报告'
                    ])
                    
                    // 归档所有产物
                    archiveArtifacts artifacts: 'reports/**/*', fingerprint: true
                    archiveArtifacts artifacts: 'models/**/*', fingerprint: true
                    
                    // 保存构建信息
                    script {
                        def accuracy = sh(
                            script: "grep -oP '\"accuracy\":\\s*\\K[0-9.]+' models/evaluation_results.json | head -1",
                            returnStdout: true
                        ).trim()
                        
                        currentBuild.description = "ML Pipeline - 准确率: ${accuracy}"
                    }
                }
            }
        }
        
        stage('生成文档') {
            steps {
                script {
                    echo '=== 生成项目文档 ==='
                    
                    // 使用writeFile直接创建文件
                    writeFile(
                        file: "${PROJECT_DIR}/build_report.md",
                        text: """# 机器学习流水线构建报告

## 构建信息
- 构建编号: ${env.BUILD_NUMBER}
- 构建时间: ${new Date().format('yyyy-MM-dd HH:mm:ss')}
- 构建状态: ${currentBuild.result ?: 'SUCCESS'}

## 数据信息
查看 data/ 目录

## 模型信息
查看 models/ 目录

## 评估结果
查看 reports/ 目录中的评估报告

## 流水线阶段
所有阶段执行完成"""
                    )
                    
                    sh '''
                        cd ''' + PROJECT_DIR + '''
                        echo "生成的报告:"
                        cat build_report.md
                        
                        # 尝试转换为HTML
                        which pandoc >/dev/null 2>&1 && pandoc build_report.md -o reports/build_report.html || echo "pandoc未安装，跳过HTML生成"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo '=== 构建完成 ==='
            echo "构建结果: ${currentBuild.result}"
        }
        success {
            echo '🎉 流水线执行成功！'
            script {
                // 简单的邮件通知（需要配置邮件）
                // emailext(
                //     subject: "✅ ML Pipeline Build #${env.BUILD_NUMBER} Success",
                //     body: "ML Pipeline build completed successfully.\n\nView: ${env.BUILD_URL}",
                //     to: 'user@example.com'
                // )
            }
        }
        failure {
            echo '❌ 流水线执行失败'
        }
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
}