#!/usr/bin/env python

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meu_projeto.settings.prod')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar o Django. Certifique-se de que está instalado."
        ) from exc
    execute_from_command_line(sys.argv)
