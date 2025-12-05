pipeline {
    agent any
    
    environment {
        VENV_DIR = "${WORKSPACE}/venv"
    }
    
    stages {
        stage('初始化环境') {
            steps {
                echo '=== 初始化环境 ==='
                sh '''
                    echo "当前目录: $(pwd)"
                    echo "Python版本: $(python3 --version 2>/dev/null || echo 'Python3 not found')"
                    echo "工作空间: ${WORKSPACE}"
                    ls -la
                '''
            }
        }
        
        stage('检出代码') {
            steps {
                checkout scm
                sh 'echo "代码检出完成" && ls -la'
            }
        }
        
        stage('创建Python环境') {
            steps {
                sh '''
                    echo "=== 创建Python虚拟环境 ==="
                    python3 -m venv ${VENV_DIR} || {
                        echo "venv失败，尝试安装virtualenv"
                        pip3 install virtualenv || python3 -m pip install virtualenv
                        python3 -m virtualenv ${VENV_DIR}
                    }
                    echo "虚拟环境创建成功"
                    ls -la ${VENV_DIR}/bin/python
                '''
            }
        }
        
        stage('安装依赖') {
            steps {
                sh '''
                    echo "=== 安装Python包 ==="
                    ${VENV_DIR}/bin/pip install --upgrade pip
                    ${VENV_DIR}/bin/pip install pandas numpy scikit-learn matplotlib seaborn joblib requests
                    echo "安装完成，包列表:"
                    ${VENV_DIR}/bin/pip list
                '''
            }
        }
        
        stage('运行机器学习流水线') {
            steps {
                sh '''
                    echo "=== 开始机器学习流水线 ==="
                    
                    echo "1. 确保目录存在..."
                    mkdir -p data/raw data/processed models reports
                    
                    echo "2. 运行数据收集..."
                    ${VENV_DIR}/bin/python scripts/data_collection.py
                    
                    echo "3. 运行数据预处理..."
                    ${VENV_DIR}/bin/python scripts/data_preprocessing.py
                    
                    echo "4. 运行模型训练..."
                    ${VENV_DIR}/bin/python scripts/train_model.py
                    
                    echo "5. 运行模型评估..."
                    ${VENV_DIR}/bin/python scripts/evaluate_model.py
                    
                    echo "=== 流水线完成 ==="
                '''
            }
        }
        
        stage('检查结果') {
            steps {
                sh '''
                    echo "=== 检查生成的文件 ==="
                    echo ""
                    echo "数据文件:"
                    find data/ -type f 2>/dev/null | sort
                    echo ""
                    echo "模型文件:"
                    find models/ -type f 2>/dev/null | sort
                    echo ""
                    echo "报告文件:"
                    find reports/ -type f 2>/dev/null | sort
                    
                    echo ""
                    echo "=== 模型评估结果 ==="
                    if [ -f "models/evaluation_results.json" ]; then
                        cat models/evaluation_results.json
                    else
                        echo "评估结果文件不存在"
                    fi
                '''
            }
            
            post {
                success {
                    echo '归档构建产物...'
                    archiveArtifacts artifacts: 'data/raw/*.csv, data/processed/*.npy, models/*.pkl, models/*.json, reports/*'
                }
            }
        }
    }
    
    post {
        always {
            echo "=== 构建完成 ==="
            echo "状态: ${currentBuild.currentResult}"
            echo "编号: ${BUILD_NUMBER}"
        }
        success {
            echo '✅ 构建成功!'
        }
        failure {
            echo '❌ 构建失败'
        }
    }
}