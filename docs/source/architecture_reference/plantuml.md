# Plantuml

The documentation uses [PlantUML](https://plantuml.com/) to render differnt diagrams.
To execute it, you do need a `*.jar` file.

To make it easier installing the `hatch run docs:install-plantuml` script can be used.
The idea is to have it download a specific version to a directory, which
is mentioned in the `docs/source/conf.py` file.

To define what version was downloaded, the `PLANTUML_VERSION` environment variable
needs to be set. To decide where the `*.jar` file will be saved, the
`PLANTUML_OUTPUT_PATH` needs to be set in the same way.

```{plantuml}

!theme sandstone

state ".gitignore" as gitignore
gitignore : Ignore everything but the "".gitkeep""
gitignore : file from the external directory.
gitignore -right-> externaldir

state "docs/external/" as externaldir
externaldir : ""plantuml.jar""
externaldir : "".gitkeep""

state "docs/source/conf.py" as confpy
confpy: Defines statically the path to the ""*.jar"" file
confpy -right-> envvars
confpy --> externaldir

state "scripts/install-plantuml.sh" as installplantumlscript
installplantumlscript : Downloads and installs the ""plantuml.jar"" using the version
installplantumlscript : and path defined in the environment variables.
installplantumlscript --> externaldir

state "pyproject.toml" as pyprojecttoml {

    state "docs-environment" as docsenvironment {

        state "env-vars" as envvars
        envvars : ""PLANTUML_VERSION""
        envvars : ""PLANTUML_OUTPUT_PATH""
        envvars --> installplantumlscript
        envvars --> externaldir

        state scripts
        scripts : ""install-plantuml""
        scripts -down-> installplantumlscript
    }
}
```
