# Style Gallery

All styles from the **scienceplots** library. Use with `--style <name>`.

| Style | Journal | Font | Characteristics |
|-------|---------|------|-----------------|
| `ieee` | IEEE | Serif | Compact, grid-lined, grayscale-friendly |
| `nature` | Nature | Sans-serif | Minimal, clean, muted colors |
| `springer` | Springer | Serif | Traditional, clear labels |
| `aaas` | Science/AAAS | Sans-serif | Compact, data-dense |
| `science` | Science | Sans-serif | Minimalist, thin spines |
| `lancet` | The Lancet | Serif | Bold, clinical, high contrast |
| `acs` | ACS | Sans-serif | Modern, colorful accents |
| `aps` | APS | Serif | Physics-style, clean presentation |

## Color Palettes

Each style comes with a curated 7-color palette for multi-series charts.

### IEEE
`#0072BD` `#D95319` `#EDB120` `#7E2F8E` `#77AC30` `#4DBEEE` `#A2142F`

### Nature
`#E64B35` `#4DBBD5` `#00A087` `#3C5488` `#F39B7F` `#8491B4` `#91D1C2`

### Lancet
`#00468B` `#ED0000` `#42B540` `#0099B4` `#525252` `#7F6F00` `#ED7D31`

### Science / AAAS
`#3B4992` `#EE0000` `#008B45` `#631879` `#008280` `#BB0021`

## Usage Notes

- **scienceplots installed**: Styles are loaded from the scienceplots library for maximum fidelity.
- **scienceplots not installed**: Built-in approximations are used (still publication-quality, but less precise to the original journal templates).
- Install scienceplots: `pip install SciencePlots`
- HTML pages may need `\usepackage{siunitx}` for LaTeX-style rendering - the skill handles this automatically in PNG/SVG output.
