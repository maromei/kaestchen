#!/bin/bash

github_releases_url="https://github.com/plantuml/plantuml/releases/download"
jar_filename="plantuml-${PLANTUML_VERSION}.jar"
download_link="${github_releases_url}/v${PLANTUML_VERSION}/${jar_filename}"

curl -L $download_link -o ${PLANTUML_OUTPUT_PATH}/plantuml.jar
