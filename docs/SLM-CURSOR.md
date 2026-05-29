# SLM en Cursor

**SLM** (*Small Language Model*) designa modelos compactos y rápidos, optimizados para tareas concretas (autocompletado, ediciones locales) en lugar de razonamiento largo sobre todo el repositorio.

## Modelos SLM relevantes en Cursor

| Modelo / modo | Uso típico | Ventaja |
|---------------|-----------|---------|
| **cursor-small** (Tab) | Predicción inline mientras escribes | Latencia muy baja (~sub-200 ms) |
| **Composer / Composer 2** | Edición multi-paso en Agent | Más barato que modelos frontera en tareas repetitivas |
| **Modelos locales** (p. ej. vía Ollama) | Privacidad o coste cero en tu máquina | Requiere configuración en Cursor Settings → Models |

Los modelos frontera (Claude, GPT, Gemini, etc.) siguen siendo la mejor opción para arquitectura, refactors grandes y planes multi-archivo.

## Cómo elegir en la práctica

1. **Tab (autocompletado)** — Deja el SLM integrado; no hace falta cambiar modelo a cada línea.
2. **Cmd+K (edición local)** — SLM o modelo rápido cuando el cambio está acotado a un fragmento.
3. **Agent (Cmd+I)** — SLM/Composer para tareas mecánicas; modelo grande para diseño, depuración difícil o muchos archivos.

Regla práctica: elige primero el **nivel de autonomía** (Tab → inline → Agent) y después el **modelo**.

## Modelos locales (opcional)

Si quieres un SLM en tu hardware:

1. Instala [Ollama](https://ollama.com) (u otro servidor compatible).
2. Descarga un modelo pequeño orientado a código (p. ej. variantes de Code Llama, Qwen Coder, DeepSeek Coder en tamaño reducido).
3. En Cursor: **Settings → Models** y añade el endpoint/base URL de tu servidor local.
4. Selecciona ese modelo solo para tareas donde la latencia o el coste importen más que el contexto largo.

## Relación con este repositorio

**SLM CURSOR** centraliza notas y, más adelante, código de ejemplo sobre cuándo usar SLM frente a modelos grandes. Cuando añadas una app (p. ej. Angular según `.gitignore`), documenta aquí qué modelo usaste en CI o en agentes de fondo para cada tipo de tarea.
