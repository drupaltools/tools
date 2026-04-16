# SCSS Compilation for Viewer

## Overview

The web viewer uses SCSS for styling. SCSS files are compiled to CSS using libsass.

## Structure

```
static/
├── scss/
│   ├── viewer.scss       # Main stylesheet
│   └── _*.scss          # Partials (future use)
└── css/
    └── viewer.css       # Compiled output (auto-generated)
```

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

This installs `libsass` and `watchdog` needed for SCSS compilation.

### Compile SCSS (One-Time)

```bash
# Using make
make scss

# Or directly
python3 src/compile_scss.py
```

### Watch Mode (Auto-Compile on Changes)

```bash
# Using make
make scss-watch

# Or directly
python3 src/compile_scss.py --watch
```

Watch mode automatically recompiles whenever you save changes to SCSS files.

### Start Viewer with Auto-Compilation

```bash
# Compile SCSS and start viewer
make viewer
```

## Development Workflow

1. **Edit SCSS**: Make changes to `static/scss/viewer.scss`
2. **Watch Mode**: Run `make scss-watch` in a terminal
3. **Run Viewer**: Run `make viewer` in another terminal
4. **Refresh Browser**: Changes appear on page refresh

## SCSS Features Used

- **Variables**: Colors, spacing, fonts defined at top
- **Nesting**: Organize related styles
- **Mixins**: Reusable style patterns (transitions, shadows)
- **Responsive**: Media queries for mobile devices

## Customization

### Change Colors

Edit variables at the top of `viewer.scss`:

```scss
$primary-color: #0678be;      // Main brand color
$secondary-color: #333;        // Text color
$background-color: #f5f5f5;   // Page background
```

### Add New Styles

Add new styles to `viewer.scss` following the existing structure:

```scss
.my-component {
  padding: $spacing-md;
  background: $primary-color;

  &:hover {
    opacity: 0.8;
  }
}
```

### Create Partials

For large stylesheets, split into partials:

1. Create `_variables.scss`, `_mixins.scss`, etc.
2. Import in `viewer.scss`: `@import 'variables';`
3. Partials (files starting with `_`) are not compiled directly

## Output

- **Compression**: CSS is minified for production
- **Location**: Compiled CSS in `static/css/viewer.css`
- **Git**: CSS files are gitignored (compile on deployment)

## Troubleshooting

### SCSS won't compile

```bash
# Check if libsass is installed
pip show libsass

# Reinstall if needed
pip install --upgrade libsass
```

### Watch mode not detecting changes

```bash
# Check if watchdog is installed
pip show watchdog

# Reinstall if needed
pip install --upgrade watchdog
```

### Syntax errors

Check the error message from the compiler:
- Line numbers point to error location
- Common: missing semicolons, unclosed brackets

### CSS not updating in browser

- Hard refresh: Ctrl+Shift+R (Linux/Windows) or Cmd+Shift+R (Mac)
- Check browser console for CSS loading errors
- Verify `viewer.css` exists in `static/css/`

## Clean Build

Remove all compiled CSS:

```bash
make clean
```

Then recompile:

```bash
make scss
```
