pipeline {
    agent any
    
    tools {
        python3 'Python3'
    }
    
    environment {
        // 项目路径
        PROJECT_DIR = "${WORKSPACE}/ml-automation-pipeline"
        
        // Python虚拟环境
        VENV_PATH = "${PROJECT_DIR}/venv"
        
        // 报告路径
        REPORTS_DIR = "${PROJECT_DIR}/reports"
        MODELS_DIR = "${PROJECT_DIR}/models"
        DATA_DIR = "${PROJECT_DIR}/data"
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
                        source ${VENV_PATH}/bin/activate
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
                        source ${VENV_PATH}/bin/activate
                        
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
                        source ${VENV_PATH}/bin/activate
                        
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
                        source ${VENV_PATH}/bin/activate
                        
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
                        source ${VENV_PATH}/bin/activate
                        
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
                    
                    sh """
                        cd ${PROJECT_DIR}
                        
                        # 创建构建报告
                        cat > build_report.md << EOF
                        # 机器学习流水线构建报告
                        
                        ## 构建信息
                        - 构建编号: ${BUILD_NUMBER}
                        - 构建时间: $(date)
                        - 构建状态: ${currentBuild.result ?: 'SUCCESS'}
                        
                        ## 数据信息
                        \$(ls -la data/raw/ && echo "" && ls -la data/processed/)
                        
                        ## 模型信息
                        \$(ls -la models/)
                        
                        ## 评估结果
                        \$(cat models/evaluation_results.json | python3 -m json.tool | head -50)
                        
                        ## 流水线阶段
                        \$(echo "所有阶段执行完成")
                        EOF
                        
                        # 转换为HTML
                        pandoc build_report.md -o reports/build_report.html || echo "pandoc未安装，跳过HTML生成"
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo '=== 构建完成 ==='
            echo "构建结果: ${currentBuild.result}"
            
            // 清理工作空间（可选）
            // cleanWs()
        }
        success {
            echo '🎉 流水线执行成功！'
            emailext(
                subject: "✅ ML流水线构建 #${BUILD_NUMBER} 成功",
                body: "机器学习流水线构建 #${BUILD_NUMBER} 执行成功。\n\n查看报告: ${BUILD_URL}report\n\n模型准确率: 查看附件报告",
                to: 'your-email@example.com',
                attachmentsPattern: 'reports/**/*.html,reports/**/*.png'
            )
        }
        failure {
            echo '❌ 流水线执行失败'
            emailext(
                subject: "❌ ML流水线构建 #${BUILD_NUMBER} 失败",
                body: "机器学习流水线构建 #${BUILD_NUMBER} 执行失败。\n\n查看日志: ${BUILD_URL}console",
                to: 'your-email@example.com'
            )
        }
        unstable {
            echo '⚠️ 流水线执行不稳定'
        }
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
}