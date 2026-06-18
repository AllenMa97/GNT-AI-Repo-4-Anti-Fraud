# Paper Directory

This directory contains the paper drafts in multiple formats and templates.

## Directory Structure

```
paper/
├── README.md                    # This file
├── 论文纲要_中文.md             # Chinese paper outline
├── 论文纲要_英文.md             # English paper outline
├── figures/                     # Paper figures
│   ├── design-philosophy.md     # Visual design philosophy
│   ├── generate_figures.py      # Figure generation script
│   ├── tapf_architecture.svg    # Main architecture diagram
│   ├── data_pipeline.svg        # Data construction pipeline
│   └── experiment_results.svg   # Experiment results
├── aaai25/                      # AAAI 2025 LaTeX template
│   ├── main.tex                 # Main paper file
│   └── references.bib           # Bibliography
├── neurips/                     # NeurIPS template (placeholder)
└── latex_template/             # Generic LaTeX templates
```

## How to Use

### Generate Figures

```bash
cd figures
python generate_figures.py
```

This will generate SVG versions of the paper figures. To convert to PDF for the paper:

```bash
# Using Inkscape (recommended)
inkscape tapf_architecture.svg -A tapf_architecture.pdf
inkscape data_pipeline.svg -A data_pipeline.pdf
inkscape experiment_results.svg -A experiment_results.pdf
```

### Compile AAAI Paper

```bash
cd aaai25
pdflatex main.tex
bibtex main.aux
pdflatex main.tex
pdflatex main.tex
```

### Figure Files

| File | Description |
|------|-------------|
| `tapf_architecture.svg/pdf` | Main TAPF framework architecture |
| `data_pipeline.svg/pdf` | 4-layer data construction pipeline |
| `experiment_results.svg/pdf` | Experiment results visualization |

## Design Philosophy

Figures follow the "Data Sentinel" visual philosophy:
- Deep indigo (#1e3a5f): Raw data, unprocessed information
- Cyan (#00d4ff): Filtered output, trusted information
- Amber (#ffb800): Decision points, critical boundaries
- Monospace typography for technical labels
- Concentric geometry representing information layers
