# aind-mesoscope-user-schema-ui

A small tool for use after mesoscope sessions. Generates aind-data-schema compliant session.json and data_description.csv, and writes a transfer manifest for aind-watchdog-service.

## Deployment

Deployment uses `uv tool install`, and is set up with an ansible playbook in the SIPE deployment system.

The uv-tool deployment scheme is described [here](https://github.com/AllenNeuralDynamics/SIPE-Admin/discussions/141) and is based on this command
`uv tool install git+https://github.com/AllenNeuralDynamics/aind-mesoscope-user-schema-ui.git@refactor`

## Usage

If installed via uv tool (and UV_TOOL_BIN_DIR on path):
- `meso-prepare-transfer.exe --username "Patrick Latimer" --session-id "610489749"`

If you do not pass in arguments, ~~it will open the GUI and prompt you to enter name and session id~~

## Configuration

Configuration pulls at runtime from SIPE's configuration server (http://eng-tools:8888/api/v1beta/configs/projects/meso_prepare_transfer), which uses zookeeper as a storage backend.

Config files are cached at C:/ProgramData/AllenInstitute/meso_prepare_transfer/config/config_server_response.json

## Logging

Logs are sent to a file at C:/ProgramData/AllenInstitute/meso_prepare_transfer/logs/meso_prepare_transfer.log as well as sent to the SIPE log server that can be viewed here: http://eng-logtools:8080/?channel_filter=meso_prepare_transfer&hide=location,count

## Development

Clone the repo.

Install dependencies with `uv sync`

Run with `uv run meso-prepare-transfer --username "Patrick Latimer" --session-id "610489749"`