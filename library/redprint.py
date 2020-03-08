class RedPrint(object):
    def __init__(self, name):
        self.name = name
        self.mound = []

    def route(self, rule, **options):
        def decorator(f):
            self.mound.append((rule, f, options))
            return f
        return decorator

    def register(self, blueprint, url_prefix=None):
        if not url_prefix:
            url_prefix = f"/{self.name}"
        for rule, f, options in self.mound:
            endpoint = options.pop("endpoint", f.__name__)
            blueprint.add_url_rule(url_prefix + rule, endpoint, f, **options)
