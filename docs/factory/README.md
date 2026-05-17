# Factory Extension for Kanvas

## Objetivo
Extender Kanvas para soportar una software factory multiagente, manteniendo el proyecto:
- agnóstico al motor
- git-friendly
- centrado en Obsidian + Markdown
- gobernado por estados y contratos

## Decisión de diseño
Kanvas seguirá siendo la base visual y de workflow. La capa factory añadirá:
- estados funcionales más ricos
- contratos de rol
- tickets Markdown por ID
- supervisor/orchestrator
- sincronización canvas <-> markdown

## Principios
- **No backend oculto**: la fuente de verdad vive en archivos del repo.
- **Canvas para visión global**.
- **Markdown para detalle y trazabilidad**.
- **El supervisor valida transiciones; los agentes proponen**.
- **No acoplarse a Claude/Codex/Gemini**.

## MVP
1. Parsear tarjetas canónicas de canvas
2. Parsear tickets Markdown
3. Resolver routing por estado
4. Exponer `factory status`
5. Exponer `factory dispatch --dry-run`
6. Exponer `factory sync`
