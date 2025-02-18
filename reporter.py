import os
from datetime import datetime
from pathlib import Path
import pandas as pd
from tabulate import tabulate
from jinja2 import Template

class TestReporter:
    def __init__(self, results, test_message):
        self.results = results
        self.test_message = test_message
        self.report_dir = Path(__file__).parent / 'test_reports'
        self.report_dir.mkdir(exist_ok=True)
        
    def create_report(self):
        """Create and save test report"""
        # 创建时间戳
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 准备数据
        data = []
        for result in self.results:
            if result:  # 如果测试成功
                data.append({
                    'Provider': result.provider,
                    'First Token (s)': f"{result.first_token_time:.2f}" if result.first_token_time else "-",
                    'Reasoning Tokens': result.reasoning_tokens if result.reasoning_tokens > 0 else "-",
                    'Reasoning Time (s)': f"{result.reasoning_time:.2f}" if result.reasoning_tokens > 0 else "-",
                    'Content Tokens': result.content_tokens if result.content_tokens > 0 else "-",
                    'Content Time (s)': f"{result.content_time:.2f}" if result.content_tokens > 0 else "-",
                    'Total Tokens': result.total_tokens,
                    'Total Time (s)': f"{result.total_time:.2f}",
                    'Tokens/s': f"{result.total_tokens / result.total_time:.2f}" if result.total_time > 0 else "-"
                })
            else:  # 如果测试失败
                data.append({
                    'Provider': "Failed",
                    'First Token (s)': "-",
                    'Reasoning Tokens': "-",
                    'Reasoning Time (s)': "-",
                    'Content Tokens': "-",
                    'Content Time (s)': "-",
                    'Total Tokens': "-",
                    'Total Time (s)': "-",
                    'Tokens/s': "-"
                })
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 生成HTML报告
        html_report = self._generate_html_report(df, timestamp)
        
        # 保存报告
        report_path = self.report_dir / f'test_report_{timestamp}'
        
        # 保存CSV
        df.to_csv(f'{report_path}.csv', index=False)
        
        # 保存HTML
        with open(f'{report_path}.html', 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        # 打印表格到控制台
        print("\n测试结果总结：")
        print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
        print(f"\n详细报告已保存到：{report_path}.html 和 {report_path}.csv")
        
        return report_path
    
    def _generate_html_report(self, df, timestamp):
        """Generate HTML report using template"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>API Testing Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { margin-bottom: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                .metadata { margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>API Testing Report</h1>
                <div class="metadata">
                    <p><strong>Test Time:</strong> {{ timestamp }}</p>
                    <p><strong>Test Message:</strong> {{ test_message }}</p>
                </div>
            </div>
            {{ table }}
        </body>
        </html>
        """
        
        # 渲染模板
        template = Template(template)
        html = template.render(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            test_message=self.test_message,
            table=df.to_html(index=False)
        )
        
        return html
