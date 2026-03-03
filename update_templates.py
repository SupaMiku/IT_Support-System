# script to overwrite tickets.html with new Jinja2 version
content = '''{% extends 'base.html' %}

{% block title %}Tickets – School IT Support System{% endblock %}

{% block page_heading %}Ticket Management{% endblock %}
{% block page_sub %}Track, assign and resolve IT support requests{% endblock %}

{% block topbar %}
<div class="search-box"><span>🔍</span><input type="text" placeholder="Search tickets…" oninput="filterTable(this.value)"/></div>
<button class="icon-btn"><span class="notif-dot"></span>🔔</button>
<div class="topbar-avatar">{{ current_user.username[:2].upper() if current_user }}</div>
{% endblock %}

{% block content %}
<!-- Stats -->
<div class="stats-row">
  <div class="stat-mini" style="--d:.05s"><div class="stat-mini__icon" style="background:rgba(224,168,64,.12)">🎫</div><div><div class="stat-mini__val">{{ ticket_stats.open }}</div><div class="stat-mini__label">Open</div></div></div>
  <div class="stat-mini" style="--d:.1s"> <div class="stat-mini__icon" style="background:rgba(122,179,212,.12)">🔄</div><div><div class="stat-mini__val">{{ ticket_stats.in_progress }}</div><div class="stat-mini__label">In Progress</div></div></div>
  <div class="stat-mini" style="--d:.15s"><div class="stat-mini__icon" style="background:rgba(76,175,130,.12)">✔</div><div><div class="stat-mini__val">{{ ticket_stats.resolved }}</div><div class="stat-mini__label">Resolved</div></div></div>
  <div class="stat-mini" style="--d:.2s"> <div class="stat-mini__icon" style="background:rgba(224,85,85,.12)">⚠</div><div><div class="stat-mini__val">{{ ticket_stats.critical }}</div><div class="stat-mini__label">Critical</div></div></div>
</div>

<!-- Toolbar -->
<div class="toolbar">
  <div class="toolbar-left">
    <select class="filter-select" onchange="applyFilter()">
      <option value="">All Status</option>
      <option>Open</option><option>In Progress</option><option>Resolved</option>
    </select>
    <select class="filter-select" onchange="applyFilter()">
      <option value="">All Priority</option>
      <option>Critical</option><option>High</option><option>Medium</option><option>Low</option>
    </select>
    <select class="filter-select" onchange="applyFilter()">
      <option value="">All Category</option><option>Hardware</option><option>Network</option><option>Software</option><option>Account</option>
    </select>
  </div>
  <div class="toolbar-right">
    <button class="btn btn-primary" onclick="openModal('createModal')">➕ New Ticket</button>
  </div>
</div>

<!-- Table -->
<div class="panel">
  <div class="panel__head">
    <span class="panel__title">All Tickets</span>
    <div class="panel__actions"></div>
  </div>
  <div style="overflow-x:auto">
    <table class="data-table" id="ticketTable">
      <!-- rows populated via JS/API -->
    </table>
  </div>
</div>

{% endblock %}
'''
with open('templates/tickets.html','w',encoding='utf-8') as f:
    f.write(content)
print('tickets.html updated')
