(architecture_logging)=
# Logging

The general issue when it comes to logging, is that we want to make modifications based
on some [settings](#architecture_configuration).
The {py:class}`kaestchen.loggers.LoggingManager` is desined to handle that.
Basic configurations are done in the {py:mod}`kaestchen.loggers` module itself.
It contains dictionaries with the templates for the configuration.
The `LoggingManager` then applies modifications and to copies of these objects,
and passes them to the python logging framework.

```{plantuml}

!theme mars
hide empty description

state "Configuration Templates / Base" as configtemplates {
    state "FORMATTERS_BASE" as formatter_base
    state "HANDLERS_BASE" as handlers_base
    state "LOGGERS_BASE" as loggers_base
    state "LOGGING_CONFIG_BASE" as logging_config_base
}

configtemplates -down-> loggingmanager.configdicts
note left on link
    ""LoggingManager._ _init_ _()""

    Copies the base templates
    to the manager object.
endnote

state "class LoggingManager" as loggingmanager {

    state "Config Dictionaries" as configdicts {
        configdicts : ""formatters""
        configdicts : ""handlers""
        configdicts : ""loggers""
        configdicts : ""logging_config""
    }

    state "Asemble Functions" as asemblefunctions {

        state "assemble_formatters()\nassemble_handlers()\nassemble_loggers()" as subassemblefunctions
        state "assemble_config()" as assemble_config

        assemble_config -up-> subassemblefunctions : calls
    }

    asemblefunctions -left-> configdicts : Builds\nand\nmodifies

    state "@staticmethod\nsetup_logging()" as setup_logging #palegreen;line.bold;line:green {
        setup_logging : Uses the built config to initialize
        setup_logging : ""logging.config.dictConfig(config)""
    }

    setup_logging -left-> asemblefunctions
}

state "Python native logging module" as nativelogging #line.dotted
loggingmanager.setup_logging -down[dotted]-> nativelogging

```

## Notes on Modifying the logging config

- **`filename` entries in file handlers are always relative to the `logdir`**
  - The `logdir` refers to a setting, which can be set via environment variables
    or a config file.
- **If no `logdir` is specified, every file handler is replaced with a `NullHandler`**
- **The parent directory of `logdir` needs to exist**
  - The `logdir` will be created if it does not exist.
  - The parent directory will not be created. Instead, an error will be raised.
