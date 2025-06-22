# General Idea

- be a dumb excel
- it is annoying that excel tries to do too much
- just have cells with some content

## Storage

- simply open `*.csv` files (`feature:extensions.csv`)
- also have `*.kaestchen` file extension (`feature:extensions.kaestchen`)
    - contains simple meta information
    - either refer to an external `*.csv` file, or embed `*.csv` file.
      - (`feature:extensions.kaestchen.external_csv`, `feature:extensions.kaestchen.embedded_csv`)

## Column Config

- All the configuration should be done on the header of a cell-column (`feature:column_config`)
- Configs should be simple
- Configs could include:
    - Set format via regex (`feature:column_config.regex_format`)
        - so f.e. you can set a date format
        - non conforming inputs should not be saved
    - Set mode to markdown (`feature:column_config.render_markdown`)
        - markdown is rendered in the cell
    - cell expand (`feature:column_config.expand_cell`)
        - cell can be small, and expands to full size on click

## Editing / Viewing

- There should be a small toggle / select for editing/viewing (`feature:ui.editing_viewing_toggle`)
- The column config dialog should not be permanently visible (`feature:ui.column_config.hide`)
- You should be able to edit a cell in a separate window (`ui.editing.new_window`)
