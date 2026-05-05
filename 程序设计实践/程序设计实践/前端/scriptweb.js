// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const checkRiskBtn = document.getElementById('checkRiskBtn');
    const selfEvaluationBtn = document.getElementById('selfEvaluationBtn');
    const inputText = document.getElementById('inputText');
    const alertDialog = document.getElementById('alertDialog');
    const selfEvaluationDialog = document.getElementById('selfEvaluationDialog');
    const overlay = document.getElementById('overlay');
    const closeAlertBtn = document.getElementById('closeAlertBtn');
    const emergencyBtn = document.getElementById('emergencyBtn');
    const customContextMenu = document.getElementById('customContextMenu');
    const checkSelectionRisk = document.getElementById('checkSelectionRisk');
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const closeButtons = document.querySelectorAll('.close-btn');
    const submitAssessment = document.getElementById('submitAssessment');
    const resetAssessment = document.getElementById('resetAssessment');
    const assessmentForm = document.getElementById('assessmentForm');
    const assessmentResult = document.getElementById('assessmentResult');
    const backToAssessment = document.getElementById('backToAssessment');
    const saveResult = document.getElementById('saveResult');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    // 显示弹窗的函数
    function showDialog(dialog) {
        dialog.style.display = 'block';
        overlay.style.display = 'block';
        setTimeout(() => {
            dialog.classList.add('show');
            overlay.style.opacity = '1';
        }, 10);
    }
    
    // 隐藏弹窗的函数
    function hideDialog(dialog) {
        dialog.classList.remove('show');
        overlay.style.opacity = '0';
        setTimeout(() => {
            dialog.style.display = 'none';
            overlay.style.display = 'none';
        }, 300);
    }
    
    // 更新进度条
    function updateProgress() {
        const totalQuestions = 16;
        let answered = 0;
        
        for (let i = 1; i <= totalQuestions; i++) {
            if (document.querySelector(`input[name="q${i}"]:checked`)) {
                answered++;
            }
        }
        
        const progress = (answered / totalQuestions) * 100;
        progressFill.style.width = `${progress}%`;
        progressText.textContent = `${answered}/${totalQuestions} 已完成`;
    }
    
    // 为所有单选按钮添加事件监听
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', updateProgress);
    });
    
    // 检测文本风险 - 修改为调用后端API
    checkRiskBtn.addEventListener('click', function() {
        const text = inputText.value.trim();
        
        if (text === '') {
            alert('请输入要检测的文本！');
            return;
        }
        
        // 显示加载状态
        checkRiskBtn.disabled = true;
        checkRiskBtn.textContent = '检测中...';
        
        // 调用后端API
        fetch('http://127.0.0.1:5000/api/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('服务器响应异常');
            }
            return response.json();
        })
        .then(result => {
            // 更新弹窗内容
            document.getElementById('detectedText').textContent = text.length > 100 ? text.substring(0, 100) + '...' : text;
            document.getElementById('riskLevel').textContent = result.risk || '未知';
            document.getElementById('riskLevel').className = 'info-value ' + getRiskClass(result.risk || '未知');
            document.getElementById('riskDescription').textContent = result.reason || '无法获取风险描述';
            document.getElementById('riskRecommendations').textContent = result.advice || '无建议';
            
            // 根据风险等级设置图标
            const riskIcon = document.getElementById('riskIcon');
            if (result.risk === '高危' || result.risk === '高风险') {
                riskIcon.textContent = '🚨';
            } else if (result.risk === '中危' || result.risk === '中风险') {
                riskIcon.textContent = '⚠️';
            } else {
                riskIcon.textContent = '✅';
            }
            
            // 显示弹窗
            showDialog(alertDialog);
        })
        .catch(error => {
            console.error('检测失败:', error);
            // 出错时使用本地模拟检测
            const riskLevel = getRiskLevel(text);
            const riskDescription = getRiskDescription(riskLevel);
            const recommendations = getRecommendations(riskLevel);
            
            // 更新弹窗内容
            document.getElementById('detectedText').textContent = text.length > 100 ? text.substring(0, 100) + '...' : text;
            document.getElementById('riskLevel').textContent = riskLevel;
            document.getElementById('riskLevel').className = 'info-value ' + getRiskClass(riskLevel);
            document.getElementById('riskDescription').textContent = riskDescription + '\n(本地模式)';
            document.getElementById('riskRecommendations').textContent = recommendations;
            
            // 根据风险等级设置图标
            const riskIcon = document.getElementById('riskIcon');
            if (riskLevel === '高风险') {
                riskIcon.textContent = '🚨';
            } else if (riskLevel === '中风险') {
                riskIcon.textContent = '⚠️';
            } else {
                riskIcon.textContent = '✅';
            }
            
            // 显示弹窗
            showDialog(alertDialog);
        })
        .finally(() => {
            // 恢复按钮状态
            checkRiskBtn.disabled = false;
            checkRiskBtn.textContent = '检测风险';
        });
    });
    
    // 显示风险评估自测弹窗
    selfEvaluationBtn.addEventListener('click', function() {
        showDialog(selfEvaluationDialog);
        // 重置进度
        updateProgress();
    });
    
// 关闭弹窗
    closeAlertBtn.addEventListener('click', function() {
        hideDialog(alertDialog);
    });
    
    // 紧急处理按钮
    emergencyBtn.addEventListener('click', function() {
        alert('紧急处理建议：\n1. 立即停止与可疑人员的联系\n2. 不要进行任何转账操作\n3. 立即拨打110或96110报警\n4. 联系银行冻结相关账户');
    });
    
    // 点击遮罩层关闭弹窗
    overlay.addEventListener('click', function() {
        hideDialog(alertDialog);
        hideDialog(selfEvaluationDialog);
    });
    
    // 关闭按钮事件
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const dialog = this.closest('.dialog');
            hideDialog(dialog);
        });
    });
    
    // 自定义右键菜单
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        
        const selectedText = window.getSelection().toString().trim();
        if (selectedText.length > 0) {
            customContextMenu.style.display = 'block';
            customContextMenu.style.left = e.pageX + 'px';
            customContextMenu.style.top = e.pageY + 'px';
        }
    });
    
    // 点击其他地方隐藏右键菜单
    document.addEventListener('click', function() {
        customContextMenu.style.display = 'none';
    });
    
    // 检测选中文本风险
    checkSelectionRisk.addEventListener('click', function() {
        const selectedText = window.getSelection().toString().trim();
        
        if (selectedText) {
            inputText.value = selectedText;
            checkRiskBtn.click();
        }
        
        customContextMenu.style.display = 'none';
    });
    
    // 侧边栏切换
    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('open');
    });
    
    // 提交风险评估
    submitAssessment.addEventListener('click', function() {
        // 计算风险得分
        let score = 0;
        const totalQuestions = 16;
        let allAnswered = true;
        
        for (let i = 1; i <= totalQuestions; i++) {
            const selectedOption = document.querySelector(`input[name="q${i}"]:checked`);
            if (selectedOption) {
                score += parseInt(selectedOption.value);
            } else {
                allAnswered = false;
            }
        }
        
        if (!allAnswered) {
            alert('请完成所有问题后再提交评估！');
            return;
        }
        
        // 计算风险等级
        let riskLevel, riskAnalysis, suggestions;
        const resultIcon = document.getElementById('resultIcon');
        
        if (score <= 15) {
            riskLevel = "低风险";
            riskAnalysis = "您的网络诈骗风险较低，安全意识良好。您能够较好地保护个人信息，对可疑信息保持警惕，并采取了一定的安全防护措施。继续保持良好的上网习惯，定期更新安全知识。";
            suggestions = "1. 继续保持良好的上网习惯和安全意识\n2. 定期关注最新的诈骗手段和防范方法\n3. 定期更新重要账户的密码\n4. 安装并定期更新防病毒软件\n5. 向家人朋友分享安全知识";
            resultIcon.textContent = "✅";
        } else if (score <= 30) {
            riskLevel = "中风险";
            riskAnalysis = "您存在一定的网络诈骗风险，部分上网行为可能存在安全隐患。建议加强安全意识，改进上网习惯，特别是在个人信息保护和链接点击方面需要更加谨慎。";
            suggestions = "1. 提高对可疑电话、短信和邮件的警惕性\n2. 避免在不安全的网站或公共Wi-Fi上输入个人信息\n3. 谨慎点击不明链接和下载附件\n4. 为不同账户设置不同的强密码\n5. 定期检查银行账户和信用报告\n6. 学习识别钓鱼网站和诈骗信息";
            resultIcon.textContent = "⚠️";
        } else {
            riskLevel = "高风险";
            riskAnalysis = "您的网络诈骗风险较高，上网行为存在明显安全隐患。您可能经常在不安全的环境下处理敏感信息，或对诈骗手段的识别能力有待提高。建议立即采取措施改善安全习惯，避免财产损失。";
            suggestions = "1. 立即停止与任何可疑人员的联系\n2. 不要进行任何未经核实的转账或付款操作\n3. 立即更改所有重要账户的密码\n4. 安装可靠的防病毒软件并开启实时保护\n5. 参加网络安全培训，学习常见诈骗手段\n6. 启用双重身份验证保护重要账户\n7. 如遇可疑情况，立即拨打110或96110报警";
            resultIcon.textContent = "🚨";
        }
        
        // 更新结果页面
        document.getElementById('riskScore').textContent = score + "分（满分48分）";
        document.getElementById('overallRiskLevel').textContent = riskLevel;
        document.getElementById('overallRiskLevel').className = 'info-value ' + getRiskClass(riskLevel);
        document.getElementById('riskAnalysis').textContent = riskAnalysis;
        document.getElementById('improvementSuggestions').textContent = suggestions;
        
        // 切换到结果页面
        assessmentForm.style.display = 'none';
        assessmentResult.style.display = 'block';
    });
    
    // 重置评估
    resetAssessment.addEventListener('click', function() {
        const radioButtons = document.querySelectorAll('input[type="radio"]');
        radioButtons.forEach(radio => {
            radio.checked = false;
        });
        updateProgress();
    });
    
    // 返回评估
    backToAssessment.addEventListener('click', function() {
        assessmentResult.style.display = 'none';
        assessmentForm.style.display = 'block';
    });
    
    // 保存结果
    saveResult.addEventListener('click', function() {
        alert('评估结果已保存！建议您定期进行风险评估，及时了解自己的网络安全状况。');
    });
    
    // 辅助函数：根据文本内容判断风险等级
    function getRiskLevel(text) {
        const highRiskKeywords = ['转账', '密码', '验证码', '汇款', '中奖', '保证金', '手续费', '安全账户', '涉嫌违法', '逮捕令'];
        const mediumRiskKeywords = ['优惠', '折扣', '免费', '投资', '理财', '赚钱', '兼职', '客服', '退款', '快递'];
        
        const lowerText = text.toLowerCase();
        let highRiskCount = 0;
        let mediumRiskCount = 0;
        
        highRiskKeywords.forEach(keyword => {
            if (lowerText.includes(keyword.toLowerCase())) {
                highRiskCount++;
            }
        });
        
        mediumRiskKeywords.forEach(keyword => {
            if (lowerText.includes(keyword.toLowerCase())) {
                mediumRiskCount++;
            }
        });
        
        if (highRiskCount >= 2) {
            return '高风险';
        } else if (highRiskCount >= 1 || mediumRiskCount >= 3) {
            return '中风险';
        } else {
            return '低风险';
        }
    }
    
    // 辅助函数：获取风险描述
    function getRiskDescription(riskLevel) {
        switch(riskLevel) {
            case '高风险':
                return '该文本包含多个高风险关键词，极有可能是诈骗信息。请高度警惕，不要进行任何转账或提供个人信息。';
            case '中风险':
                return '该文本包含一些可疑内容，可能存在诈骗风险。请谨慎对待，不要轻易相信其中的承诺或要求。';
            case '低风险':
                return '该文本风险较低，但仍需保持警惕。请注意保护个人信息，避免泄露敏感数据。';
            default:
                return '无法确定风险等级，请谨慎对待。';
        }
    }
    
    // 辅助函数：获取建议措施
    function getRecommendations(riskLevel) {
        switch(riskLevel) {
            case '高风险':
                return '1. 立即停止与信息发布者的联系\n2. 不要进行任何转账或汇款操作\n3. 不要提供任何个人信息或验证码\n4. 立即拨打110或96110报警\n5. 向相关平台举报该信息';
            case '中风险':
                return '1. 谨慎对待该信息，不要轻易相信\n2. 核实信息来源的真实性\n3. 不要点击不明链接或下载附件\n4. 保护个人信息，避免泄露\n5. 如有疑问，可咨询亲友或警方';
            case '低风险':
                return '1. 保持警惕，注意保护个人信息\n2. 定期更新密码，使用强密码\n3. 安装防病毒软件并定期更新\n4. 学习常见诈骗手段，提高防范意识';
            default:
                return '请保持警惕，注意保护个人信息安全。';
        }
    }
    
    // 辅助函数：获取风险等级对应的CSS类
    function getRiskClass(riskLevel) {
        switch(riskLevel) {
            case '高风险':
                return 'risk-high';
            case '中风险':
                return 'risk-medium';
            case '低风险':
                return 'risk-low';
            default:
                return '';
        }
    }
    
    // 示例文本
    inputText.value = "尊敬的用户，您的账户存在异常，请立即点击链接验证身份，否则账户将被冻结。验证需要提供您的银行卡号、密码和验证码。";
    
    // 初始化进度条
    updateProgress();
    
    // 初始化导航点击事件
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            showPage(page);
        });
    });
    
    // 初始化防诈知识功能
    initKnowledgeFeatures();
    
    // 初始化横向导航点击事件 - 直接在这里绑定
    initHorizontalNavigation();
});

// 页面切换功能
function showPage(pageId) {
    // 隐藏所有页面
    document.querySelectorAll('.page-content').forEach(page => {
        page.classList.remove('active');
    });
    
    // 显示目标页面
    const targetPage = document.getElementById(`${pageId}-page`);
    if (targetPage) {
        targetPage.classList.add('active');
        
        // 更新导航激活状态
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        const activeLink = document.querySelector(`[data-page="${pageId}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
        
        // 对于功能介绍页面，确保默认显示第一个功能详情
        if (pageId === 'features') {
            // 延迟执行，确保DOM完全加载
            setTimeout(() => {
                document.querySelectorAll('.feature-detail').forEach(detail => {
                    detail.classList.remove('active');
                });
                document.querySelectorAll('.features-horizontal-nav .features-nav-card').forEach(card => {
                    card.classList.remove('active');
                });
                
                const firstDetail = document.getElementById('text-detection-content');
                const firstNavCard = document.querySelector('.features-horizontal-nav .features-nav-card[data-feature="text-detection"]');
                
                if (firstDetail) {
                    firstDetail.classList.add('active');
                }
                if (firstNavCard) {
                    firstNavCard.classList.add('active');
                }
                
                // 重新绑定横向导航事件
                initHorizontalNavigation();
            }, 100);
        }
    }
}

// 更新进度条
function updateProgress() {
    const totalQuestions = 16;
    let answered = 0;
    
    for (let i = 1; i <= totalQuestions; i++) {
        if (document.querySelector(`input[name="q${i}"]:checked`)) {
            answered++;
        }
    }
    
    const progress = (answered / totalQuestions) * 100;
    progressFill.style.width = `${progress}%`;
    progressText.textContent = `${answered}/${totalQuestions} 已完成`;
}

// 删除第二个重复定义的initHorizontalNavigation函数，保留第一个版本
// 横向导航功能
function initHorizontalNavigation() {
    console.log('初始化横向导航...');
// 为横向导航卡片添加点击事件
    const horizontalCards = document.querySelectorAll('.features-horizontal-nav .features-nav-card');
    console.log('找到的横向导航卡片:', horizontalCards.length);
    
    horizontalCards.forEach(card => {
        // 移除之前的事件监听器
        card.replaceWith(card.cloneNode(true));
    });
    
    // 重新获取元素并绑定事件
    document.querySelectorAll('.features-horizontal-nav .features-nav-card').forEach(card => {
        card.addEventListener('click', function() {
            console.log('点击了导航卡片:', this.getAttribute('data-feature'));
            
            const feature = this.getAttribute('data-feature');
            
            // 移除所有卡片的激活状态
            document.querySelectorAll('.features-horizontal-nav .features-nav-card').forEach(c => {
                c.classList.remove('active');
            });
            
            // 添加当前卡片的激活状态
            this.classList.add('active');
            
            // 隐藏所有详情
            document.querySelectorAll('.feature-detail').forEach(detail => {
                detail.classList.remove('active');
            });
            
            // 显示对应的功能详情
            const targetDetail = document.getElementById(`${feature}-content`);
            console.log('目标详情元素:', targetDetail);
            
            if (targetDetail) {
                targetDetail.classList.add('active');
                
                // 平滑滚动到顶部
                window.scrollTo({
                    top: document.getElementById('features-page').offsetTop - 20,
                    behavior: 'smooth'
                });
            } else {
                console.error('未找到对应的功能详情:', `${feature}-content`);
            }
        });
    });
}

// 防诈知识相关功能
function initKnowledgeFeatures() {
    // 防诈知识数据
    const knowledgeData = {
        '刷单兼职诈骗': {
            title: '刷单兼职诈骗防范指南',
            description: '识别和防范虚假兼职诈骗',
            content: `
                <div class="detail-section">
                    <h4>💰 诈骗手法</h4>
                    <p>以"轻松赚钱"为诱饵，通过以下步骤实施诈骗：</p>
                    <ul>
                        <li>通过微信群、QQ群发布"日赚300-500元"等兼职广告</li>
                        <li>前几单小额返利获取信任，让受害者放松警惕</li>
                        <li>以"任务升级"、"连单任务"为由要求大额垫资</li>
                        <li>各种理由拒绝返款，最后拉黑受害者</li>
                    </ul>
                </div>
                <div class="detail-section">
                    <h4>🔍 识别特征</h4>
                    <ul>
                        <li>夸张的收入承诺："轻松月入过万"</li>
                        <li>要求先支付保证金、培训费、会员费</li>
                        <li>需要垫付资金完成所谓的"任务"</li>
                        <li>通过个人微信、支付宝转账，不走正规平台</li>
                    </ul>
                </div>
                <div class="warning-box">
                    <h5>⚠️ 重要提醒</h5>
                    <p>任何要求先付款的兼职都是诈骗！正规兼职不会要求垫资，更不会承诺不切实际的高额回报。</p>
                </div>
                <div class="protection-tips">
                    <h5>🛡️ 防范措施</h5>
                    <ul>
                        <li>通过正规平台寻找兼职工作</li>
                        <li>不轻信"轻松赚钱"的广告</li>
                        <li>不向陌生人转账或垫付资金</li>
                        <li>遇到可疑情况及时向平台举报</li>
                    </ul>
                </div>
            `
        },
        '冒充公检法': {
            title: '冒充公检法诈骗防范指南',
            description: '识别冒充执法人员的诈骗手段',
            content: `
                <div class="detail-section">
                    <h4>💰 诈骗手法</h4>
                    <p>冒充公安、检察院工作人员实施诈骗：</p>
                    <ul>
                        <li>能准确说出个人信息获取信任</li>
                        <li>声称涉嫌"洗钱"、"贩毒"等重大刑事案件</li>
                        <li>要求配合调查，将资金转入"安全账户"</li>
                        <li>威胁不配合将采取"强制措施"</li>
                    </ul>
                </div>
                <div class="detail-section">
                    <h4>🔍 识别特征</h4>
                    <ul>
                        <li>能准确报出身份证号、住址等个人信息</li>
                        <li>要求保密，不能告诉家人朋友</li>
                        <li>要求下载所谓"安全软件"或"案件查询APP"</li>
                        <li>通过电话"远程办案"，不见面处理</li>
                    </ul>
                </div>
                <div class="warning-box">
                    <h5>⚠️ 重要提醒</h5>
                    <p>公检法不会电话办案，更不会要求转账到安全账户！所有法律文书都会当面送达。</p>
                </div>
                <div class="protection-tips">
                    <h5>🛡️ 防范措施</h5>
                    <ul>
                        <li>接到此类电话立即挂断</li>
                        <li>不透露任何个人信息</li>
                        <li>不下载陌生APP或点击可疑链接</li>
                        <li>直接拨打110或反诈中心96110核实</li>
                    </ul>
                </div>
            `
        },
        '投资理财诈骗': {
            title: '投资理财诈骗防范指南',
            description: '识别虚假投资平台诈骗',
            content: `
                <div class="detail-section">
                    <h4>💰 诈骗手法</h4>
                    <p>建立虚假投资平台实施诈骗：</p>
                    <ul>
                        <li>承诺"保本保息"，回报率异常高</li>
                        <li>伪造交易记录和盈利截图</li>
                        <li>前期允许小额提现获取信任</li>
                        <li>大额投入后以各种理由无法提现</li>
                    </ul>
                </div>
                <div class="detail-section">
                    <h4>🔍 识别特征</h4>
                    <ul>
                        <li>承诺年化收益率超过10%</li>
                        <li>需要向个人账户或不明公司转账</li>
                        <li>平台无法正常提现或提现困难</li>
                        <li>不断催促加大投资力度</li>
                    </ul>
                </div>
                <div class="warning-box">
                    <h5>⚠️ 重要提醒</h5>
                    <p>选择正规金融机构投资，不轻信高回报承诺！任何投资都有风险，超高回报往往伴随超高风险。</p>
                </div>
                <div class="protection-tips">
                    <h5>🛡️ 防范措施</h5>
                    <ul>
                        <li>选择银行、证券公司等正规金融机构</li>
                        <li>不向个人账户转账进行投资</li>
                        <li>了解投资产品的真实性和合法性</li>
                        <li>保持理性，不被高收益诱惑</li>
                    </ul>
                </div>
            `
        },
        '虚假购物诈骗': {
            title: '虚假购物诈骗防范指南',
            description: '识别虚假购物平台和商品',
            content: `
                <div class="detail-section">
                    <h4>💰 诈骗手法</h4>
                    <p>通过虚假购物平台实施诈骗：</p>
                    <ul>
                        <li>商品价格明显低于市场价</li>
                        <li>要求微信、支付宝直接转账</li>
                        <li>发货后无法查询真实物流信息</li>
                        <li>收款后失联或提供假货</li>
                    </ul>
                </div>
                <div class="warning-box">
                    <h5>⚠️ 重要提醒</h5>
                    <p>选择正规电商平台交易，使用平台担保支付！不轻信过低价格，不直接向个人转账。</p>
                </div>
            `
        },
        '冒充客服诈骗': {
            title: '冒充客服诈骗防范指南',
            description: '识别冒充客服的诈骗手段',
            content: `
                <div class="detail-section">
                    <h4>📞 诈骗手法</h4>
                    <p>冒充商家客服实施诈骗：</p>
                    <ul>
                        <li>声称商品质量问题或订单异常</li>
                        <li>主动提出退款或双倍赔偿</li>
                        <li>诱导下载"退款软件"或点击钓鱼链接</li>
                        <li>以各种理由要求提供验证码或转账</li>
                    </ul>
                </div>
                <div class="warning-box">
                    <h5>⚠️ 重要提醒</h5>
                    <p>正规客服不会要求提供验证码或转账！遇到此类情况，请直接联系官方客服核实。</p>
                </div>
            `
        },
        '中奖诈骗': {
            title: '中奖诈骗防范指南',
            description: '识别虚假中奖信息',
            content: `
                <div class="detail-section">
                    <h4>🎁 诈骗手法</h4>
                    <p>以虚假中奖信息实施诈骗：</p>
                    <ul>
                        <li>通过短信、邮件、电话通知中奖</li>
                        <li>要求先支付"税费"、"手续费"、"保证金"等</li>
                        <li>提供虚假的官方网站或证书</li>
                        <li>收款后失联</li>
                    </ul>
                </div>
                <div class="warning-box">
                    <h5>⚠️ 重要提醒</h5>
                    <p>正规中奖不会要求先支付任何费用！请通过官方渠道核实中奖信息的真实性。</p>
                </div>
            `
        }
    };
    
    // 显示知识详情
    window.showKnowledgeDetail = function(type) {
        const data = knowledgeData[type] || {
            title: '防诈知识',
            description: '了解更多防范知识',
            content: '<div class="detail-section"><p>详细内容正在更新中...</p></div>'
        };
        
        const knowledgeTitle = document.getElementById('knowledge-title');
        const knowledgeDescription = document.getElementById('knowledge-description');
        const knowledgeContent = document.getElementById('knowledge-content');
        
        if (knowledgeTitle && knowledgeDescription && knowledgeContent) {
            knowledgeTitle.textContent = data.title;
            knowledgeDescription.textContent = data.description;
            knowledgeContent.innerHTML = data.content;
        }
        
        // 重置所有卡片样式
        document.querySelectorAll('#knowledge-page .feature-card').forEach(card => {
            card.classList.remove('active');
        });
        
        // 添加当前卡片激活样式
        const currentCard = document.querySelector(`[data-type="${type}"]`);
        if (currentCard) {
            currentCard.classList.add('active');
        }
    };
    
    // 为知识卡片添加点击事件
    const featureCards = document.querySelectorAll('#knowledge-page .feature-card');
    const cardTypes = ['刷单兼职诈骗', '冒充公检法', '投资理财诈骗', '虚假购物诈骗', '冒充客服诈骗', '中奖诈骗'];
    
    featureCards.forEach((card, index) => {
        if (index < cardTypes.length) {
            card.setAttribute('data-type', cardTypes[index]);
            card.addEventListener('click', function() {
                showKnowledgeDetail(cardTypes[index]);
            });
        }
    });
    
    // 初始化测试功能
    initKnowledgeTests();
}

// 防诈测试功能
function initKnowledgeTests() {
    const testButtons = document.querySelectorAll('.test-btn');
    
    testButtons.forEach(button => {
        button.addEventListener('click', function() {
            const testType = this.dataset.test;
            alert('测试功能开发中，敬请期待！');
        });
    });
}
// 删除以下重复的代码片段
//            const targetDetail = document.getElementById(`${feature}-content`);
//            console.log('目标详情元素:', targetDetail);
//            
//            if (targetDetail) {
//                targetDetail.classList.add('active');
//                
//                // 平滑滚动到顶部
//                window.scrollTo({
//                    top: document.getElementById('features-page').offsetTop - 20,
//                    behavior: 'smooth'
//                });
//            } else {
//                console.error('未找到对应的功能详情:', `${feature}-content`);
//            }
//        });
//    });
//}
//            const targetDetail = document.getElementById(`${feature}-content`);
//            console.log('目标详情元素:', targetDetail);
//            
//            if (targetDetail) {
//                targetDetail.classList.add('active');
//                
//                // 精确滚动到具体模块
//                setTimeout(() => {
//                    const targetPosition = targetDetail.offsetTop - 100; // 减去一些偏移量，让内容更可见
//                    console.log('滚动到位置:', targetPosition);
//                    
//                    window.scrollTo({
//                        top: targetPosition,
//                        behavior: 'smooth'
//                    });
//                }, 50); // 短暂延迟确保DOM更新完成
//            } else {
//                console.error('未找到对应的功能详情:', `${feature}-content`);
//            }
//        });
//    });
//}