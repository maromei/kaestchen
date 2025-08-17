# Kaestchen Object structure

- Have the general `pydantic` model with its validation seperate from the
  actual `kaestchen` class/file/object structure.

```{plantuml}

!theme sandstone

state "Kaestchen object" as kaestchenobj {

  state "Config Structure" as configstructure {

    configstructure : Represented by the ""XMLKaestchen"" class
    configstructure : ""kaestchen.config_parser.model.XMLKaestchen""

    state "Pydanctic Model" as pydanticmodel
    pydanticmodel : Basix XML strcture definition
    pydanticmodel : ""kaestchen.config_parser.model""

    state "Additional Validations" as addvalidation
    addvalidation : More complex validators
    addvalidation : ""kaestchen.config_parser.validate""

    pydanticmodel --> addvalidation
  }

  state "File Operations" as fileoperations {

    fileoperations : Read and write data represented by the ""XMLKaestchen"" class
    fileoperations : ""kaestchen.config_parser.io""

  }
}
```

## Config Structure

- Model Definition an (simple) Validation done via `pydantic`
  - See {py:mod}`kaestchen.config_parser.model`
- Complex validations are also done via pydantic, but its validators are found in a
  seperate file.
  - See {py:mod}`kaestchen.config_parser.validate`
