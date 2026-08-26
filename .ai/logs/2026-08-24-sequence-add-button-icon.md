# Sequence "Add" button: icon instead of the word "Add"

## Change
`src/templates/deform/sequence.pt` (override of deform 3.0.1 template):

- The add link no longer prints deform's `add_subitem_text` ("Add Autor Pessoal").
  It now renders a Bootstrap Icons plus glyph followed by just the subitem title
  ("<+> Autor Pessoal").
- `subitem_title` is taken from `field.children[0].title` (the sequence prototype
  item), falling back to the sequence `title` if unavailable.
- The full original text ("Add Autor Pessoal") is kept as the `title` attribute so
  it still shows as a tooltip / is available to assistive tech.
- The `${field.oid}-addtext` id is preserved, since deform.js targets it.

## Notes
- Doing this from Python (`SequenceWidget(add_subitem_text_template=...)`) does not
  work for markup: Chameleon escapes `${}`, so an `<i>` tag would be printed literally.
  Only a literal unicode glyph would work there.
- For an icon-only button, remove the `<small>` element; the tooltip already carries
  the label.
