// 夜之向日葵主题交互效果

document.addEventListener('DOMContentLoaded', function() {
    
    // 添加向日葵装饰元素
    addSunflowerDecorations();
    
    // 添加进度条
    addProgressBar();
    
    // 添加滚动效果
    addScrollEffects();
    
    // 添加向日葵按钮效果
    addSunflowerButtonEffects();
    
    // 添加工具提示
    addTooltips();
    
    // 添加页面加载动画
    addPageLoadAnimation();
});

// 添加向日葵装饰元素
function addSunflowerDecorations() {
    const body = document.body;
    
    // 创建向日葵装饰
    const sunflowerDecoration = document.createElement('div');
    sunflowerDecoration.className = 'sunflower-decoration';
    body.appendChild(sunflowerDecoration);
    
    // 创建夜晚装饰
    const nightDecoration = document.createElement('div');
    nightDecoration.className = 'night-decoration';
    body.appendChild(nightDecoration);
    
    // 随机添加更多装饰
    for (let i = 0; i < 3; i++) {
        const decoration = document.createElement('div');
        decoration.style.cssText = `
            position: fixed;
            top: ${Math.random() * 100}%;
            left: ${Math.random() * 100}%;
            font-size: ${20 + Math.random() * 20}px;
            opacity: 0.05;
            pointer-events: none;
            z-index: -1;
            animation: sunflower-float ${6 + Math.random() * 4}s ease-in-out infinite;
        `;
        decoration.innerHTML = Math.random() > 0.5 ? '🌻' : '🌙';
        body.appendChild(decoration);
    }
}

// 添加进度条
function addProgressBar() {
    const progressBar = document.createElement('div');
    progressBar.className = 'sunflower-progress';
    document.body.appendChild(progressBar);
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset;
        const docHeight = document.body.offsetHeight - window.innerHeight;
        const scrollPercent = (scrollTop / docHeight) * 100;
        progressBar.style.width = scrollPercent + '%';
    });
}

// 添加滚动效果
function addScrollEffects() {
    const cards = document.querySelectorAll('.card, .post-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });
    
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'all 0.6s ease-out';
        observer.observe(card);
    });
}

// 添加向日葵按钮效果
function addSunflowerButtonEffects() {
    const buttons = document.querySelectorAll('.md-button, .sunflower-button');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // 创建点击波纹效果
            const ripple = document.createElement('span');
            const rect = button.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255, 215, 0, 0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s ease-out;
                pointer-events: none;
            `;
            
            button.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

// 添加工具提示
function addTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.classList.add('sunflower-tooltip');
    });
}

// 添加页面加载动画
function addPageLoadAnimation() {
    const main = document.querySelector('.md-main');
    if (main) {
        main.style.opacity = '0';
        main.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            main.style.transition = 'all 0.8s ease-out';
            main.style.opacity = '1';
            main.style.transform = 'translateY(0)';
        }, 100);
    }
}

// 添加向日葵徽章
function createSunflowerBadge(text, type = 'default') {
    const badge = document.createElement('span');
    badge.className = 'sunflower-badge';
    badge.textContent = text;
    
    if (type === 'new') {
        badge.style.background = 'linear-gradient(135deg, #ff6b35 0%, #ffd700 50%, #ff8c00 100%)';
    } else if (type === 'hot') {
        badge.style.background = 'linear-gradient(135deg, #ff4757 0%, #ff6b35 50%, #ff8c00 100%)';
    }
    
    return badge;
}

// 添加向日葵加载器
function createSunflowerLoader() {
    const loader = document.createElement('div');
    loader.className = 'sunflower-loader';
    return loader;
}

// 添加向日葵卡片组
function createSunflowerCardGroup() {
    const cardGroup = document.createElement('div');
    cardGroup.className = 'sunflower-card-group';
    return cardGroup;
}

// 页面切换效果
window.addEventListener('beforeunload', function() {
    const main = document.querySelector('.md-main');
    if (main) {
        main.style.transition = 'all 0.3s ease-out';
        main.style.opacity = '0';
        main.style.transform = 'translateY(-20px)';
    }
});

// 添加键盘快捷键
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K 聚焦搜索框
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('.md-search__input');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // ESC 关闭搜索
    if (e.key === 'Escape') {
        const searchInput = document.querySelector('.md-search__input');
        if (searchInput && document.activeElement === searchInput) {
            searchInput.blur();
        }
    }
});

// 添加向日葵主题切换效果
function addThemeSwitchEffect() {
    const themeToggle = document.querySelector('[data-md-color-scheme]');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            // 添加切换动画
            document.body.style.transition = 'all 0.5s ease';
            
            setTimeout(() => {
                document.body.style.transition = '';
            }, 500);
        });
    }
}

// 添加向日葵导航效果
function addNavigationEffects() {
    const navLinks = document.querySelectorAll('.md-nav__link');
    
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(8px) scale(1.02)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0) scale(1)';
        });
    });
}

// 添加向日葵搜索效果
function addSearchEffects() {
    const searchInput = document.querySelector('.md-search__input');
    if (searchInput) {
        searchInput.addEventListener('focus', function() {
            this.style.transform = 'scale(1.02)';
        });
        
        searchInput.addEventListener('blur', function() {
            this.style.transform = 'scale(1)';
        });
    }
}

// 初始化所有效果
document.addEventListener('DOMContentLoaded', function() {
    addThemeSwitchEffect();
    addNavigationEffects();
    addSearchEffects();
});

// 添加向日葵波纹动画CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style); 