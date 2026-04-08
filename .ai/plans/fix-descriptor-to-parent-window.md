# Fix descriptor-to-parent-window bugs in annif_suggestion.html

## Context
The page `annif_suggestion.html` is a popup window for suggesting DeCS descriptors. When a user clicks "Adicionar" (Add), it sends the descriptor to the parent/opener window via `postMessage`. Several bugs prevent this from working reliably.

## Bugs to fix

### 1. No `window.opener` null guard (line 833) — HIGH
**Problem:** `window.opener.postMessage(descriptor, '*')` throws `TypeError` if `window.opener` is null (page opened directly, or opener closed).
**Fix:** Add null check before calling `postMessage`. Show user feedback if opener is unavailable.

### 2. Broken close button (line 772) — MEDIUM
**Problem:** `href="javascript:this.close()"` — `this` is the `<a>` element, not `window`.
**Fix:** Change to `javascript:window.close()` or use `onclick="window.close(); return false"`.

### 3. Duplicate IDs on primary/secondary links — MEDIUM
**Problem:** Both primary and secondary `<a>` tags share the same ID (e.g., `btn_3883_primary` for both). Invalid HTML.
**Fix:** Rename secondary link IDs to use `_secondary` suffix (e.g., `btn_3883_secondary`).

### 4. Unclosed `<td>` tags — LOW
**Problem:** Pattern `<td><strong>Name</strong><td>` appears for every descriptor row. Second `<td>` should be `</td>`.
**Fix:** Replace each unclosed `<td>` with `</td>` after the descriptor name.

### 5. Security: `postMessage` targetOrigin `'*'` — LOW (optional)
**Problem:** Any origin can intercept the message.
**Fix:** Replace `'*'` with the expected parent origin, or leave as-is if origins vary (requires user input on deployment setup).

## Files to modify
- `/tmp/annif/annif_suggestion.html`

## Changes

### In `postMsg` function (lines 832-841):
```javascript
function postMsg(descriptor, decs_id) {
    if (!window.opener) {
        alert("Erro: janela principal não encontrada.");
        return;
    }
    window.opener.postMessage(descriptor, '*');
    $("#btn_" + decs_id).attr("disabled", true);
    $("#btn_" + decs_id).addClass("disabled");
    $("#btn_icon_" + decs_id).attr("disabled", true);
    $("#btn_icon_" + decs_id).addClass("disabled");
    alert("Descritor adicionado");
}
```

### Close button (line 772):
```html
<a href="javascript:window.close()" class="btn btn-large btn-inverse align-center" role="button">Fechar</a>
```

### Duplicate IDs — for each descriptor row:
Rename the secondary link ID from `btn_XXXX_primary` to `btn_XXXX_secondary`.

### Unclosed `<td>` tags — for each descriptor row:
Change `<strong>Name</strong>\n<td>` to `<strong>Name</strong>\n</td>`.

## Verification
1. Open the page as a popup from a parent window → click "Adicionar" → descriptor should be sent via postMessage
2. Open the page directly (no opener) → click "Adicionar" → should show error message instead of crashing
3. Click "Fechar" → window should close
4. Validate HTML has no duplicate IDs and all `<td>` tags are properly closed
