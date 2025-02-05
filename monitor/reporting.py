import json
from datetime import datetime
from jinja2 import Template

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>System Report - {{ timestamp }}</title>
    <style>
        .metric-box { border: 1px solid #ddd; padding: 15px; margin: 10px; }
        .alert { color: #dc3545; }
        .metric { margin-bottom: 10px; }
    </style>
</head>
<body>
    <h1>System Health Report</h1>
    <p>Generated at: {{ timestamp }}</p>
    
    <h2>Current Metrics</h2>
    {% for metric, value in current.items() %}
    <div class="metric-box">
        <h3>{{ metric.upper() }}</h3>
        <pre>{{ value|tojson(indent=2) }}</pre>
    </div>
    {% endfor %}
    
    <h2>Alerts</h2>
    {% if alerts %}
        <ul>
        {% for alert in alerts %}
            <li class="alert">{{ alert }}</li>
        {% endfor %}
        </ul>
    {% else %}
        <p>No active alerts</p>
    {% endif %}
</body>
</html>
"""

class ReportGenerator:
    def __init__(self, monitor):
        self.monitor = monitor
        self.timestamp = datetime.now().isoformat()
        
    def generate(self, format_type):
        report_data = {
            'timestamp': self.timestamp,
            'current': self.monitor.get_system_status(),
            'history': self.monitor.history,
            'alerts': self.monitor.alerts,
            'thresholds': self.monitor.config['thresholds']
        }
        
        if format_type == 'json':
            return self._generate_json(report_data)
        elif format_type == 'html':
            return self._generate_html(report_data)
        else:
            return self._generate_text(report_data)

    def _generate_text(self, data):
        report = []
        report.append(f"System Health Report ({data['timestamp']})")
        report.append("\nCurrent Metrics:")
        for metric, value in data['current'].items():
            report.append(f"  {metric.upper():<10}: {value}")
        
        report.append("\nThresholds:")
        for metric, value in data['thresholds'].items():
            report.append(f"  {metric.upper():<10}: {value}%")
        
        report.append("\nAlerts:")
        if data['alerts']:
            for alert in data['alerts']:
                report.append(f"  - {alert}")
        else:
            report.append("  No active alerts")
            
        return "\n".join(report)

    def _generate_json(self, data):
        return json.dumps(data, indent=2, default=str)

    def _generate_html(self, data):
        template = Template(HTML_TEMPLATE)
        return template.render(
            timestamp=data['timestamp'],
            current=data['current'],
            alerts=data['alerts'],
            tojson=json.dumps
        )