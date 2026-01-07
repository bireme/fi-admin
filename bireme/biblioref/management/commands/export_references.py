# coding: utf-8
"""
Exporta References em JSON via Tastypie Resource.

Este comando exporta todos os registros do modelo Reference (biblioref.models.Reference)
usando a lógica completa do ReferenceResource (api.bibliographic.ReferenceResource),
incluindo full_dehydrate() e dehydrate() para formato idêntico à API.

FILTRO APLICADO (equivalente ao fq do get_search):
    status__in=[-3, 0, 1]

ARQUIVOS GERADOS:
    export_references_jsons/references_00000000_00000100.json
    export_references_jsons/references_00000100_00000200.json
    ...

USO:
    # Exporta tudo em chunks de 1000 (default: 100)
    python manage.py export_references 1000
    
    # Retoma exportação a partir do offset 50000
    python manage.py export_references 1000 --offset=50000
    
    # Especifica diretório customizado
    python manage.py export_references 500 --outdir=/backup/refs_json
"""

from django.core.management.base import BaseCommand
from api.bibliographic import ReferenceResource
import json
import os
import time


class Command(BaseCommand):
    help = 'Exporta toda a base do ReferenceResource em JSON, em arquivos paginados (status -3, 0, 1)'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, nargs='?', default=100)
        parser.add_argument('--offset', type=int, default=0)
        parser.add_argument(
            '--outdir',
            default='export_references_jsons',
            help='Diretório de saída dos arquivos JSON (default: export_references_jsons)'
        )

    def handle(self, *args, **options):
        resource = ReferenceResource()
        base_qs = resource._meta.queryset
        qs = base_qs.filter(status__in=[-3, 0, 1]) # filtro equivalente ao fq da API

        count = options['count']
        initial_offset = options['offset']
        outdir = options['outdir']
        os.makedirs(outdir, exist_ok=True)

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING('Nenhum registro para exportar (status -3, 0, 1)'))
            return

        # garante que o offset inicial não ultrapasse o total
        if initial_offset >= total:
            self.stdout.write(
                self.style.WARNING(f'Offset inicial {initial_offset} >= total {total}. Nada para exportar.')
            )
            return

        total_exported = 0
        i = 0
        for slice_from in range(initial_offset, total, count):
            t0 = time.time() # início do timer

            slice_to = min(slice_from + count, total)

            objects = list(qs[slice_from:slice_to])
            if not objects:
                continue

            data = []
            for obj in objects:
                bundle = resource.build_bundle(obj=obj, request=None)
                bundle = resource.full_dehydrate(bundle)
                bundle = resource.dehydrate(bundle)
                data.append(bundle.data)

            filename = f"references_{slice_from:08d}_{slice_to:08d}.json"
            filepath = os.path.join(outdir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, default=str)

            exported_now = len(data)
            total_exported += exported_now
            i += 1

            dt = time.time() - t0  # fim do timer

            self.stdout.write(
                self.style.SUCCESS(
                    f'Chunk {i}: exportados {exported_now} registros de um total de {total}'
                    f' (status -3, 0, 1) para {filepath} em {dt:.2f}s'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Exportação concluída. Total de registros exportados: {total_exported} de {total}'
            )
        )