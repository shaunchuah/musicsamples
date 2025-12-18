# api_v3/views/__init__.py
# Aggregates v3 API view exports for convenient imports by routers and other modules.
# Exists to provide a clear import surface for the dedicated api_v3 app.

from api_v3.views.auth import CurrentUserView  # noqa: F401
from api_v3.views.samples import SampleV3ViewSet  # noqa: F401
