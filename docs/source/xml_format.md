# XML Reference

```xml
<kaestchen>
    <format_version>{FORMAT_VERSION}</format_version>
    <sheets>
        <sheet name="{SHEET_NAME}" order="{SHEET_ORDER}">
            <column_config>
                <column name="{COLUMN_NAME}">
                    <renderer type="{RENDERER_TYPE}">
                        {RENDERER_SETTINGS}
                    </renderer>
                    <expand_cell enabled="{EXPAND_CELL_ENABLED}">
                        {EXPAND_CELL_SETTINGS}
                    </expand_cell>
                </column>
                ...
            </column_config>
            <csv type="{CSV_TYPE}">
                {CSV_CONTENT}
            </csv>
        </sheet>
        ...
    </sheets>
</kaestchen>
```

- `<kaestchen>...</kaestchen>`
  - The Root Element. Can have multiple `<sheet>` tags.
- `<format_version>...</format_version>`
  - Which version of this `kaestchen-xml` format is used.
    Should there every be some tags or defaults which change meaning over time,
    this tag should be used to identify these inconsistencies.
- `<sheet>...</sheet>`
  - Datasheet. One CSV / One dataset.
  - `SHEET_NAME`:
    - Name of the sheet
  - `SHEET_ORDER`
    - Order of the sheet from left to right. Left is lower id.
      Have integer datatype.
- `<column_config>...</column_config>`
  - Contains Settings for the individual columns.
    Can have multiple `<column>` tags.
- `<column>...</column>`
  - Contains META information about the given columns. F.e. types or regex
    behaviour can be set here. Note that not every column needs to have
    a config entry. Only if special rules should be applied, it can be found
    here.
    - `COLUMN_NAME`:
      - The column name to which the config is assigned to. In case the
- `<renderer>...</renderer>`
  - A column config. Defines how the value should be rendered.
  - Does not need to be included.
  - `RENDERER_TYPE`
    - Which renderer to use. Possible values are: `markdown`, `default`
    - The `default` renderer is implied. Simply removing the entire `<renderer>`
      tag would have the same effect.
    - `markdown` renders valid markown.
  - `RENDERER_SETTINGS` can contain settings for rendering. Depends on the type.
- `<expand_cell>...</expand_cell>`
  - A column config. Defines that the cell is displayed in small, but can be
    expanded to reveal the full data.
  - Optional.
  - `EXPAND_CELL_ENABLED`:
    - Either `0` or `1`. If the cell is not present, `0` (off) is assumed.
  - `EXPAND_CELL_SETTINGS`:
    - Settings.
- `<csv>...</csv>`
  - Contains the actual data.
  - `CSV_TYPE`:
    - Either `inline` or `external`. Determines what `CSV_CONTENT` will be
      interpreted as.
  - `CSV_CONTENT`:
    - If `CSV_TYPE=inline`, `CSV_CONTENT` will contain the csv data just pasted
      in there. If `CSV_TYPE=external`, it will be interpreted as the path
      to the csv file. If it is a relative path, it will be taken relative to
      the `*.kaestchen` file.

