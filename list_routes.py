from main import create_app
app=create_app()
print('urlpatterns:')
for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
    print(f"{rule.rule} -> {rule.endpoint}")
