(architecture_configuration)=
# Configuration

There are 3 possible ways of specifying settings in a programmable way:
CLI, environment variables and a settings file.

All three methods serve a different purpose.
The CLI is supposed to manage operations on specific files.
Environment Variables are more of a dev-tool for setting very specific things.
The settings file should mainly be a way for the user to specify behaviour, which
persists over multiple sessions.

There might still be some overlap between the three different methods.
To avoid clashes, the settings are applied via the following hirarchy:

1. CLI
2. Environment Variables<br>
    2.1. Actual environment variables<br>
    2.2. `.env` file
3. Settings file

## Seperation of Concerns

Generally, the goal is to not have an object managing the environment variables
at the same time as the settings file and the cli, as the implementation might be
entirely different.

The idea for implementing this, is to have a seperate objects responsible for
each settings method.
Then, a single object - {py:class}`kaestchen.conf.Settings` - acts as a container
for them, using computed attributes to return the actual settings values.
The computed attribtues are supposed to handle the logic of potential
configuration clashes from the different method.

```{plantuml}
@startuml

!theme mars
hide empty members
left to right direction

skinparam linetype ortho
skinparam linetype <<diamond>> curvy

package "kaestchen.conf" as kaestchenconfmodule {
    class Settings {
        -- References to settings sources --
        env_variables : EnvironmentSettings
        settings_file : SettingsFile
        cli_settings : CLISettings
        -- Computed Variables --
        log_path: str
        ...
    }

    package "Handle different sources" <<Rectangle>> {
        class EnvironmentSettings
        class SettingsFile
        class CLISettings
    }

    <> diamond

    Settings::settings_file -- diamond
    Settings::log_path .. diamond
    note top on link
        Resolve potential settings
        conflicts through
        the references.
    end note

    diamond -- EnvironmentSettings
    diamond -- SettingsFile
    diamond -- CLISettings

    entity settings
    settings - Settings

    note top of settings
        Instantiated Settings object
        to be imported and used directly.
    end note
}
@enduml
```

(Feature: {feature}`kaestchen.conf.separation_of_concerns`)

## CLI

In the current state, there is no concrete plan for the CLI.

## Environment Variables

To make the settings configuration easy, `kaestchen` uses
`pydantic-settings` as its base for configuring settings defined
via environment varibles.

(Feature: {feature}`kaestchen.conf.EnvironmentSettings`)

**1. Environment variables need to have the `KAESTCHEN_` prefix.**

The goal is to not pollute any environment with 'unknown'/'unclear' variables
names.

(Feature: {feature}`kaestchen.conf.EnvironmentSettings.prefix`)

**2. Environment Varibles should be specified in ALL CAPS.**

While the {py:class}`kaestchen.conf.EnvironmentSettings` class is setup to not be
case sensitive, it is clearer that these variables are constants, and it
fits better into the naming pattern of most other applications.

To have better typing / explicit naming of environment variables, the
{py:class}`kaestchen.conf.EnvKeys` enum can be used.

### .env file

(Feature: {feature}`kaestchen.conf.EnvironmentSettings.dotenv`)

The {py:class}`kaestchen.conf.EnvironmentSettings` class is setup to always look
in the current working directory for the `.env` file, if the `KAESTCHEN_DOTENV_FILE`
environment variable is not set.

Should, however, `KAESTCHEN_DOTENV_FILE` be explicitely defined in the environment,
but the file does not exist, an error will be raised.
The reasoning is that since the path was explicitely defined, the information of an
it being invalid should be made transparent.

(Feature: {feature}`kaestchen.conf.EnvironmentSettings.dotenv.invalid_path`)

```{plantuml}

!theme mars
hide empty description

state "Environment Variables" as envvars {
    envvars : ""KAESTCHEN_DOTENV_FILE=...""
}

state "EnvironmentSettings" as envsettings {
    state "KAESTCHEN_DOTENV_FILE is defined" as dotenvpathdefined {
        state "File Exists" as explicitfileexists
        state "File Does Not Exist" as explicitfiledoesnotexist
    }

    state "KAESTCHEN_DOTENV_FILE is not defined" as dotenvpathnotdefined {
        state "File Exists" as implicitfileexists
        state "File Does Not Exist" as implicitfiledoesnotexist
    }
}

state "Load .env" as loaddotenv

envsettings.dotenvpathdefined.explicitfileexists --> loaddotenv
envsettings.dotenvpathnotdefined.implicitfileexists --> loaddotenv

state "Raise error" as raiseerror {
    raiseerror : ""DotEnvFileDoesNotExist""
}

envsettings -[hidden]-> raiseerror

envvars -down-> envsettings
envsettings.dotenvpathdefined.explicitfiledoesnotexist -down-> raiseerror
envsettings.dotenvpathnotdefined.implicitfiledoesnotexist --> [*]
loaddotenv --> [*]
raiseerror --> [*]

```

(architecture_config_settingsfile)=
## Settings File

In the current state, there is no concrete plan for the settings file.
