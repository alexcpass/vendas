<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Python - LinkedIn Cover</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #f0f0f0;
            padding: 20px;
        }
        
        .cover {
            width: 1200px;
            height: 628px;
            background: linear-gradient(135deg, #0a1929 0%, #1a2332 50%, #0a1929 100%);
            position: relative;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        /* Elementos decorativos */
        .circle {
            position: absolute;
            border-radius: 50%;
            opacity: 0.1;
        }
        
        .circle1 {
            width: 300px;
            height: 300px;
            background: #1f77b4;
            top: -100px;
            right: -100px;
        }
        
        .circle2 {
            width: 200px;
            height: 200px;
            background: #2ca02c;
            bottom: -50px;
            left: 100px;
        }
        
        .circle3 {
            width: 150px;
            height: 150px;
            background: #ff7f0e;
            top: 200px;
            right: 200px;
        }
        
        /* Grid de fundo */
        .grid {
            position: absolute;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
            background-size: 50px 50px;
        }
        
        /* Conteúdo principal */
        .content {
            position: relative;
            z-index: 2;
            padding: 60px 80px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 40px;
        }
        
        .icon {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #1f77b4, #2ca02c);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
        }
        
        .badge {
            background: rgba(31, 119, 180, 0.2);
            color: #64b5f6;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            border: 1px solid rgba(100, 181, 246, 0.3);
        }
        
        .main-text {
            flex: 1;
        }
        
        .question {
            font-size: 52px;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.2;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .highlight {
            color: #64b5f6;
            position: relative;
        }
        
        .subtitle {
            font-size: 28px;
            color: #b0bec5;
            font-weight: 400;
            margin-bottom: 30px;
        }
        
        .solution {
            background: rgba(31, 119, 180, 0.15);
            border-left: 4px solid #1f77b4;
            padding: 20px 30px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }
        
        .solution-title {
            font-size: 18px;
            color: #64b5f6;
            font-weight: 600;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .tech-stack {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        
        .tech-item {
            background: rgba(255,255,255,0.1);
            color: #ffffff;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .footer {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }
        
        .author {
            color: #90a4ae;
            font-size: 16px;
        }
        
        .author-name {
            color: #ffffff;
            font-weight: 600;
            font-size: 18px;
        }
        
        .stats {
            display: flex;
            gap: 30px;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: #64b5f6;
        }
        
        .stat-label {
            font-size: 12px;
            color: #90a4ae;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Gráfico decorativo */
        .chart-decoration {
            position: absolute;
            right: 80px;
            top: 50%;
            transform: translateY(-50%);
            opacity: 0.15;
        }
        
        .bar {
            width: 40px;
            background: #1f77b4;
            margin: 0 8px;
            border-radius: 4px 4px 0 0;
            display: inline-block;
            vertical-align: bottom;
        }
    </style>
</head>
<body>
    <div class="cover">
        <div class="grid"></div>
        <div class="circle circle1"></div>
        <div class="circle circle2"></div>
        <div class="circle circle3"></div>
        
        <div class="chart-decoration">
            <div class="bar" style="height: 180px;"></div>
            <div class="bar" style="height: 120px;"></div>
            <div class="bar" style="height: 100px;"></div>
            <div class="bar" style="height: 200px;"></div>
            <div class="bar" style="height: 140px;"></div>
        </div>
        
        <div class="content">
            <div class="header">
                <div class="icon">📊</div>
                <div class="badge">PROJETO DE PORTFÓLIO</div>
            </div>
            
            <div class="main-text">
                <h1 class="question">
                    E se a empresa não tiver<br>
                    <span class="highlight">Power BI ou Metabase?</span>
                </h1>
                
                <p class="subtitle">
                    Criando dashboards interativos só com Python
                </p>
                
                <div class="solution">
                    <div class="solution-title">✨ Solução Completa em Python</div>
                    <div class="tech-stack">
                        <span class="tech-item">Python + Pandas</span>
                        <span class="tech-item">Streamlit</span>
                        <span class="tech-item">GitHub</span>
                        <span class="tech-item">Deploy Gratuito</span>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <div class="author">
                    <div class="author-name">Alexandre C. Passos</div>
                    <div>Analista de Dados | BI | SQL | Python</div>
                </div>
                
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-value">100%</div>
                        <div class="stat-label">Python</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">R$ 0</div>
                        <div class="stat-label">Custo</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">24/7</div>
                        <div class="stat-label">Online</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
