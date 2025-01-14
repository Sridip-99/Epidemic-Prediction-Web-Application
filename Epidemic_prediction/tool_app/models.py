from django.db import models

class ToolPermission(models.Model):
    class Meta:
        permissions = [
            ("access_tool", "Can access the prediction tool"),
            ("access_result_view", "Can access the result_view"),
        ]
