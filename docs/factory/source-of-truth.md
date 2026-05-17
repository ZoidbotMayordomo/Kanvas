# Source of Truth Policy

## Decisión adoptada
Modelo híbrido por campos:
- **Canvas manda** en el estado visible y operativo.
- **Markdown manda** en el detalle explicativo y la trazabilidad larga.

## Campos autoritativos del Canvas
- título del ticket
- estado funcional
- estado de ejecución
- rol actual
- prioridad
- doc asociado
- dependencias
- bloqueo

Estos campos se sincronizan hacia `tickets/*.md` con `sync --write`.

## Campos autoritativos del Markdown
- descripción
- criterios de aceptación
- contexto
- decisiones
- implementación
- QA / security
- historial narrativo
- siguiente paso esperado

## Implicación operativa
- `dispatch` puede reclamar tickets cambiando `Execution` a `running` en el canvas y sincronizando ese cambio al markdown.
- `sync --write` corrige en markdown los campos gobernados por canvas, sin tocar el contenido narrativo.
