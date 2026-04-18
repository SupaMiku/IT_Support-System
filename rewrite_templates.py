import os

# mapping of target file to new content
files = {
    'templates/tickets.html': """{% extends 'base.html' %}

{% block title %}Legacy Tickets Page{% endblock %}

{% block content %}
<p>The old tickets page has been replaced. Please go to <a href=\"{{ url_for('tickets_page') }}\">the tickets dashboard</a>.</p>
{% endblock %}
""",
    'templates/users.html': """{% extends 'base.html' %}
{% block title %}Legacy Users Page{% endblock %}
{% block content %}
<p>Use the <a href=\"{{ url_for('users_page') }}\">new user management</a> page.</p>
{% endblock %}
""",
    'templates/kb.html': """{% extends 'base.html' %}
{% block title %}Legacy Knowledge Base{% endblock %}
{% block content %}
<p>Knowledge base moved to <a href=\"{{ url_for('kb_page') }}\">kb dashboard</a>.</p>
{% endblock %}
""",
    'templates/announcements.html': """{% extends 'base.html' %}
{% block title %}Legacy Announcements{% endblock %}
{% block content %}
<p>Go to the <a href=\"{{ url_for('announcements_page') }}\">announcements page</a>.</p>
{% endblock %}
""",
    'templates/assets.html': """{% extends 'base.html' %}
{% block title %}Legacy Assets Page{% endblock %}
{% block content %}
<p>The assets page has been replaced. Visit <a href=\"{{ url_for('assets_page') }}\">Asset Inventory</a>.</p>
{% endblock %}
""",

}

for path, content in files.items():
    dirpath = os.path.dirname(path)
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {path}")
