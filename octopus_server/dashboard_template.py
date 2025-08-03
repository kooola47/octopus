DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Octopus Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
    <style>
        body { padding: 2rem; background: #f8fafc; }
        .table td, .table th { vertical-align: middle; }
        .form-inline input, .form-inline select { margin-right: 0.5rem; }
        .section-title { margin-top: 2rem; }
        .octopus-header { background: #4f46e5; color: #fff; padding: 1rem 2rem; border-radius: 0.5rem; }
        .octopus-header h1 { margin: 0; font-size: 2.2rem; }
        .octopus-card { background: #fff; border-radius: 0.5rem; box-shadow: 0 2px 8px #0001; padding: 1.5rem; margin-bottom: 2rem; }
        .octopus-table th { background: #6366f1; color: #fff; }
        .octopus-table tr:nth-child(even) { background: #f1f5f9; }
        .octopus-table tr:hover { background: #e0e7ff; }
        .octopus-btn { border-radius: 0.25rem; }
        .octopus-section-title { color: #4f46e5; }
        @media (max-width: 1200px) {
            .octopus-card { padding: 1rem; }
        }
        @media (max-width: 991px) {
            .row { flex-direction: column !important; }
            .col-lg-8, .col-lg-4 { max-width: 100%; flex: 0 0 100%; }
            .octopus-card { margin-bottom: 1.5rem; }
        }
        @media (max-width: 600px) {
            body { padding: 0.5rem; }
            .octopus-header { padding: 1rem; font-size: 1.2rem; }
            .octopus-card { padding: 0.5rem; }
            .octopus-section-title { font-size: 1.1rem; }
            table { font-size: 0.92rem; }
        }
    </style>
    <script>
        // Only auto-refresh if not focused on a form input
        let refreshInterval = null;
        function startAutoRefresh() {
            refreshInterval = setInterval(function() {
                if (!document.activeElement || document.activeElement.tagName === "BODY") {
                    window.location.reload();
                }
            }, 10000);
        }
        function stopAutoRefresh() {
            if (refreshInterval) clearInterval(refreshInterval);
        }
        window.onload = function() {
            startAutoRefresh();
            // Pause auto-refresh when any input/select/textarea is focused
            document.querySelectorAll('input,select,textarea').forEach(function(el) {
                el.addEventListener('focus', stopAutoRefresh);
                el.addEventListener('blur', startAutoRefresh);
            });
        };
    </script>
</head>
<body>
    <div class="octopus-header mb-4 d-flex align-items-center justify-content-between flex-wrap">
        <h1>🐙 Octopus Dashboard</h1>
        <span class="fs-5">Auto refresh every 10s</span>
    </div>
    <div class="row gx-3 gy-3">
        <div class="col-lg-8 col-12">
            <div class="octopus-card">
                <h3 class="octopus-section-title">Tasks</h3>
                <table class="table octopus-table table-bordered table-hover align-middle">
                    <thead>
                        <tr>
                            <th>ID</th><th>Type</th><th>Owner</th><th>Plugin</th><th>Action</th>
                            <th>Args</th><th>Kwargs</th>
                            <th>Start</th><th>End</th><th>Interval</th>
                            <th>Status</th><th>Executor</th>
                            <th>Result</th>
                            <th>Executions</th>
                            <th>Updated</th><th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                    {% for tid, task in tasks.items() %}
                    <tr>
                        <form method="post" action="{{ url_for('dashboard') }}">
                        <td><input name="id" value="{{ tid }}" readonly class="form-control-plaintext"></td>
                        <td>
                            <select name="type" class="form-select form-select-sm">
                                <option value="Adhoc" {% if task.get('type') == 'Adhoc' %}selected{% endif %}>Adhoc</option>
                                <option value="Schedule" {% if task.get('type') == 'Schedule' %}selected{% endif %}>Schedule</option>
                            </select>
                        </td>
                        <td><input name="owner" value="{{ task['owner'] }}" class="form-control form-control-sm"></td>
                        <td><input name="plugin" value="{{ task['plugin'] }}" class="form-control form-control-sm"></td>
                        <td><input name="action" value="{{ task['action'] }}" class="form-control form-control-sm"></td>
                        <td><input name="args" value="{{ task['args'] }}" class="form-control form-control-sm"></td>
                        <td><input name="kwargs" value="{{ task['kwargs'] }}" class="form-control form-control-sm"></td>
                        <td>
                            <input name="execution_start_time" type="datetime-local"
                                value="{{ task.get('execution_start_time', '') }}"
                                class="form-control form-control-sm">
                        </td>
                        <td>
                            <input name="execution_end_time" type="datetime-local"
                                value="{{ task.get('execution_end_time', '') }}"
                                class="form-control form-control-sm">
                        </td>
                        <td><input name="interval" value="{{ task.get('interval', '') }}" class="form-control form-control-sm"></td>
                        <td>{{ task['status'] }}</td>
                        <td>{{ task['executor'] }}</td>
                        <td style="max-width:200px;word-break:break-all;">{{ task['result'] }}</td>
                        <td>
                            {% if task['owner'] == 'ALL' and task.get('executions') %}
                                <ul style="padding-left: 1em; margin: 0;">
                                {% for exec in task['executions'] %}
                                    <li>
                                        <b>{{ exec['client'] }}</b>:
                                        <span class="badge bg-{{ 'success' if exec['status']=='success' else ('danger' if exec['status']=='failed' else 'secondary') }}">
                                            {{ exec['status'] }}
                                        </span>
                                        {% if exec['result'] %}<br><small>{{ exec['result'] }}</small>{% endif %}
                                    </li>
                                {% endfor %}
                                </ul>
                            {% endif %}
                        </td>
                        <td>{{ task['updated_at'] | datetimeformat }}</td>
                        <td>
                            <button type="submit" class="btn btn-sm btn-primary octopus-btn">Update</button>
                            <a href="{{ url_for('delete_task_ui', task_id=tid) }}" class="btn btn-sm btn-danger octopus-btn">Delete</a>
                        </td>
                        </form>
                    </tr>
                    {% endfor %}
                    </tbody>
                </table>
                <h5 class="mt-4">Add New Task</h5>
                <form method="post" action="{{ url_for('dashboard') }}" class="row g-2 align-items-center">
                    <div class="col-auto">
                        <select name="type" class="form-select form-select-sm">
                            <option value="Adhoc">Adhoc</option>
                            <option value="Schedule">Schedule</option>
                        </select>
                    </div>
                    <div class="col-auto">
                        <select name="owner" class="form-select form-select-sm" onchange="if(this.value=='__manual__'){this.style.display='none';document.getElementById('owner_manual').style.display='inline-block';document.getElementById('owner_manual').focus();}">
                            {% for owner in owner_options %}
                                <option value="{{ owner }}">{{ owner }}</option>
                            {% endfor %}
                            <option value="__manual__">Manual Input...</option>
                        </select>
                        <input id="owner_manual" name="owner" placeholder="owner" class="form-control form-control-sm" style="display:none;">
                    </div>
                    <div class="col-auto">
                        <select name="plugin" class="form-select form-select-sm" onchange="if(this.value=='__manual__'){this.style.display='none';document.getElementById('plugin_manual').style.display='inline-block';document.getElementById('plugin_manual').focus();}">
                            {% for plugin in plugin_names %}
                                <option value="{{ plugin }}">{{ plugin }}</option>
                            {% endfor %}
                            <option value="__manual__">Manual Input...</option>
                        </select>
                        <input id="plugin_manual" name="plugin" placeholder="plugin" class="form-control form-control-sm" style="display:none;">
                    </div>
                    <div class="col-auto">
                        <input name="action" placeholder="action" value="run" class="form-control form-control-sm">
                    </div>
                    <div class="col-auto">
                        <!-- Args: comma separated input -->
                        <input name="args" placeholder='args (comma separated, e.g. 1,2,3)' class="form-control form-control-sm">
                    </div>
                    <div class="col-auto">
                        <!-- Kwargs: key=value per line -->
                        <textarea name="kwargs" rows="1" placeholder='kwargs (key=value per line)' class="form-control form-control-sm" style="min-width:120px"></textarea>
                    </div>
                    <div class="col-auto">
                        <input name="execution_start_time" type="datetime-local" placeholder="start time" class="form-control form-control-sm">
                    </div>
                    <div class="col-auto">
                        <input name="execution_end_time" type="datetime-local" placeholder="end time" class="form-control form-control-sm">
                    </div>
                    <div class="col-auto"><input name="interval" placeholder="interval" class="form-control form-control-sm"></div>
                    <div class="col-auto"><button type="submit" class="btn btn-success btn-sm octopus-btn">Add Task</button></div>
                </form>
                <script>
                    // If user leaves manual input empty, revert to dropdown
                    document.addEventListener('DOMContentLoaded', function() {
                        var ownerManual = document.getElementById('owner_manual');
                        if(ownerManual){
                            ownerManual.addEventListener('blur', function(){
                                if(!this.value){
                                    this.style.display='none';
                                    this.previousElementSibling.style.display='inline-block';
                                }
                            });
                        }
                        var pluginManual = document.getElementById('plugin_manual');
                        if(pluginManual){
                            pluginManual.addEventListener('blur', function(){
                                if(!this.value){
                                    this.style.display='none';
                                    this.previousElementSibling.style.display='inline-block';
                                }
                            });
                        }
                    });
                </script>
            </div>
        </div>
        <div class="col-lg-4 col-12">
            <div class="octopus-card">
                <h3 class="octopus-section-title">Clients</h3>
                <table class="table octopus-table table-bordered table-hover align-middle">
                    <thead>
                        <tr>
                            <th>Username</th><th>Hostname</th><th>IP</th>
                            <th>Last Heartbeat</th><th>Since Last Heartbeat</th><th>Login Time</th>
                        </tr>
                    </thead>
                    <tbody>
                    {% for key, client in clients.items() %}
                    <tr>
                        <td>{{ client['username'] }}</td>
                        <td>{{ client['hostname'] }}</td>
                        <td>{{ client['ip'] }}</td>
                        <td>
                            {% if client['last_heartbeat'] %}
                                {{ client['last_heartbeat'] | datetimeformat }}
                            {% else %}
                                -
                            {% endif %}
                        </td>
                        <td>
                            {% if client['last_heartbeat'] %}
                                {{ (now - client['last_heartbeat']) | seconds_to_human }}
                            {% else %}
                                -
                            {% endif %}
                        </td>
                        <td>
                            {% if client['login_time'] %}
                                {{ client['login_time'] | datetimeformat }}
                            {% else %}
                                -
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Instructions for using the create_incident plugin -->
    <div class="octopus-card mt-4">
        <h3 class="octopus-section-title">Instructions: Using the create_incident Plugin</h3>
        <div class="mb-3">
            <strong>In the dashboard UI, to call the create_incident plugin, fill the "Add New Task" form as follows:</strong>
            <ul>
                <li>Type: Adhoc (or Schedule if you want to schedule it)</li>
                <li>Owner: (ALL, Anyone, or a specific username)</li>
                <li>Plugin: create_incident</li>
                <li>Action: run</li>
                <li>Args: [] (or e.g. ["arg1", "arg2"] if your plugin expects positional arguments)</li>
                <li>Kwargs: {} (or e.g. {"incident_type": "network"} if your plugin expects keyword arguments)</li>
                <li>Execution Start/End/Interval: as needed</li>
            </ul>
        </div>
        <div>
            <strong>Example for a simple call:</strong>
            <pre>
Type: Adhoc
Owner: ALL
Plugin: create_incident
Action: run
Args: []
Kwargs: {}
            </pre>
        </div>
        <div>
            <strong>If your plugin expects keyword arguments, for example:</strong>
            <pre>
Kwargs: {"incident_type": "network", "priority": "high"}
            </pre>
        </div>
    </div>
</body>
</html>
"""