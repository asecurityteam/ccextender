<a id="markdown-ccextender---cookiecutter-extender" name="ccextender---cookiecutter-extender"></a>
# CCExtender - Cookiecutter Extender

<!-- TOC -->

- [CCExtender - Cookiecutter Extender](#ccextender---cookiecutter-extender)
    - [Overview](#overview)
    - [Usage](#usage)
        - [For Shells Other than `bash`](#for-shells-other-than-bash)
    - [Generate A New Project From Templates](#generate-a-new-project-from-templates)
    - [Adding Commands](#adding-commands)

<!-- /TOC -->

<a id="markdown-overview" name="overview"></a>
## Overview

CCExtender, or CCX, is a docker image that provides templatized repository creation, building off the open-source Cookiecutter application. It's key difference from typical templating software is it's ability to create logical build paths, with branching logic.

Features

```bash
ccextender
    help
    --ccx_config, -c <Path to configuration file>
    --std_template, -s <Path to template containing defaults for your standards> (See #standards)
    --test_mode, -t #Activates test mode (which disables prompts for stdin)
    --outdir, -o <Path to desired repository location>
```

<a id="markdown-overview" name="overview"></a>
## Usage

To pull CCExtender from docker hub:

```bash
docker pull registry.hub.docker.com/asecurityteam/ccextender:v1
```

```bash
export DIR="$(pwd)"
docker run -v ${DIR}:/go/src/mirror/ -ti registry.hub.docker.com/asecurityteam/ccextender:v1
```

If you would like to call it as bash function, add this to your .bashrc:

```bash
ccextender() {
    local DIR
    DIR="$(pwd)"
    docker run -v ${DIR}:/go/src/mirror/ -ti registry.hub.docker.com/asecurityteam/ccextender:v1
}
```

Essentially, assuming you've setup calling the container with the alias ccextender, use will look like this:

1. Create a configuration file.

Your configuration file will contain the logic for your interactive build, directions to the templates you plan to use, and what templatized changes should be associated with your decisions.

By default, ccextender will look for a file named ccextender.yaml in your current directory, but you can direct it to read any file through the --ccx_config flag:

```bash
ccextender --ccx_config=/Users/me/Documents/myconfig.yaml
```

Your configuration file must follow the YAML format. To see how to write a CCExtender config file, see #Configuration.

2. Run CCExtender

Once the configuration file is created, CCExtender will do the rest. All that remains is for you to respond to the prompts established in your YAML file.

Examples of use:

To read in a particular configuration file and write the output to a different directory:
```bash
ccextender -c /Users/me/Documents/SecDev_Build.yaml -o /python/src/github.com/asecurityteam/
```

To see available commands:
```bash
ccextender help
```

To use a specific template for the default values for your standards (#standards):
```bash
ccextender -s template-standards
```

NOTE: This isn't a path or location of the template, but merely the template's directory name. You should add the templates location in the configuration file under the "locations" section.(#configuration)

To run using the default variables:

```bash
ccextender
```
The default values for each command is:

```bash
--ccx_config, -c = ccextender.yaml
--std_template, -s = template-standards
--test_mode, -t = None
--outdir, -o = .
```

## Configuration Files

Sample config file, ccextender.yaml:

```yaml
CCX_Version: 1.0
standard-context:
  - project_name
  - project_slug
  - project_description
  - notification_email
  - project_namespace
decisions:
  benthos:
    query:
      prompt: "Would you like to install [1] a single benthos image or [2] a benthos IO setup?"
    benthos:
      - benthos
      - gateway
    benthos-IO:
      - benthos-outbound
      - benthos-inbound
  gateway:
    query:
      prompt: "Would you like to [1] install a gateway image?"
      exclude-if:
        - benthos-IO
    gateway:
      - gateway
change-packs:
  benthos:
    template-makefile:
      image_name: "BENTHOS_IMAGE_NAME := $(APP_IMAGE_NAME)-benthos"
      hack_name: "MICROS_HACK_ARTIFACT_BENTHOS := docker.atl-paas.net$(IMAGE_PATH)/$(BENTHOS_IMAGE_NAME)"
      artifact_name: "BENTHOS_ARTIFACT_NAME=$(MICROS_HACK_ARTIFACT_BENTHOS) \\"
    template-benthos:
    template-micros:
      compose: "benthos:\n
              \   image: ${BENTHOS_ARTIFACT_NAME}\n
              \   tag: ${ARTIFACT_VERSION}\n
              \   deployRestartCount: 3\n
              \   links:\n
              \     - gateway\n
              \     - statsd-service-sidecar\n
              \   ports:\n
              \     - \"4195:4195\""
      service: "benthos:\n
              \   build:\n
              \     context: .\n
              \     dockerfile: benthos.Dockerfile\n
              \     args:\n
              \       REGISTRY: ${REGISTRY}\n
              \   image: ${IMAGE}-benthos:${TAG}"
  benthos-inbound:
    template-makefile:
      image_name: "BENTHOS_INPUT_IMAGE_NAME := $(APP_IMAGE_NAME)-benthos-input"
      hack_name: "MICROS_HACK_ARTIFACT_BENTHOS_INPUT_IMAGE_NAME := docker.atl-paas.net$(IMAGE_PATH)/$(BENTHOS_INPUT_IMAGE_NAME)"
      artifact_name: "BENTHOS_INPUT_ARTIFACT_NAME=$(MICROS_HACK_ARTIFACT_BENTHOS_INPUT_IMAGE_NAME)"
  benthos-outbound:
    template-makefile:
      image_name: "BENTHOS_OUTPUT_IMAGE_NAME := $(APP_IMAGE_NAME)-benthos-output"
      hack_name: "MICROS_HACK_ARTIFACT_BENTHOS_OUTPUT_IMAGE_NAME := docker.atl-paas.net$(IMAGE_PATH)/$(BENTHOS_OUTPUT_IMAGE_NAME)"
      artifact_name: "BENTHOS_OUTPUT_ARTIFACT_NAME=$(MICROS_HACK_ARTIFACT_BENTHOS_OUTPUT_IMAGE_NAME) \\"
  gateway:
    template-makefile:
      image_name: "Makefile Placeholder Gateway"
    template-micros:
      image_name: "Placeholder"
    template-gateway:
      image_name: "Placeholder"
locations:
  home:
    - /go/src/ccextender/pkg/ccextender/configs/
  template-makefile:
    - $!home$
    - template-makefile/
  template-gateway:
    - $!home$
    - template-gateway/
  template-micros:
    - $!home$
    - template-micros/
  template-benthos:
    - $!home$
    - template-benthos/
  template-standards:
    - $!home$
    - template-standards/
```

Let's break down this file section by section:

CCX Version

```yaml
CCX_Version: 1.0
```

While not necessary to run ccextender at the moment, future versions of ccextender might use different setups for their config files, and this value will become critical to how ccextender treats the file.

Standards

```yaml
standard-context:
  - project_name
  - project_slug
  - project_description
  - notification_email
  - project_namespace
```

Standards are variables that are common to all (or most) of our cookiecutter templates. In a multi-template build using regular cookiecutter, you'd have to answer these prompts over and over again, typing out the exact same responses by hand.

By listing these variables here, you will only have to provide values for them once for all templates you are using. Their default values will be retrieved from the template-standards cookiecutter template (or whichever template you specify).

Decisions:

```yaml
decisions:
  benthos:
    query:
      prompt: "Would you like to install [1] a single benthos image or [2] a benthos IO setup?"
    benthos:
      - benthos
      - gateway
    benthos-IO:
      - benthos-outbound
      - benthos-inbound
  gateway:
    query:
      prompt: "Would you like to [1] install a gateway image?"
      include-if:
        - benthos
      exclude-if:
        - benthos-IO
    gateway:
      - gateway
```

The Decisions section is the core of your build's logic. Here, you'll provide a series of "decision blocks", configuration units that consist of a query block, logical flags, and a series of options.

Query block:

```yaml
query:
      prompt: "Would you like to [1] install a gateway image?"
      include-if:
        - benthos
      exclude-if:
        - benthos-IO
```

The query block contains a:

prompt - your question string to the user, where you give them numerical values to choose from. Since ccextender uses an ordered yaml, the numerical responses correspond to the list of options in ascending order. As in, when looking at:

```yaml
query:
    prompt: "Would you like to install [1] a single benthos image or [2] a benthos IO setup?"
benthos:
    - benthos
    - gateway
benthos-IO:
    - benthos-outbound
    - benthos-inbound
```

... the "benthos" option would correspond to a '1' response and "benthos-IO" would correspond to a '2' response.

conditions - these conditions rely on the user's previous decisions. Depending on how the conditions resolve, ccextender might choose to skip or include a prompt in the build. Currently, the only conditions include-if and exclude-if (to see about how to add more see #FutureDevelopment).

Condition logic

include-if - If the user has made one of the below decisions, run this decision             block.

exclude-if - If the user has made one of the below decision, don't run this                 decision block.

Options:

```yaml
benthos:
    query:
      prompt: "Would you like to install [1] a single benthos image or [2] a benthos IO setup?"
    benthos:
      - benthos
      - gateway
    benthos-IO:
      - benthos-outbound
      - benthos-inbound
```

In the above snippet, "benthos" and "benthos-IO" are options. When the user receives the prompt, their response will correlate with one of the options (or skip if the input 0, and the default value if they give no response).

Each option has a list pointing to various changepacks, which hold the bundles templatized changes that will build the repository.

Changepacks:

```yaml
change-packs:
  benthos:
    template-makefile:
      image_name: "BENTHOS_IMAGE_NAME := $(APP_IMAGE_NAME)-benthos"
      hack_name: "MICROS_HACK_ARTIFACT_BENTHOS := docker.atl-paas.net$(IMAGE_PATH)/$(BENTHOS_IMAGE_NAME)"
      artifact_name: "BENTHOS_ARTIFACT_NAME=$(MICROS_HACK_ARTIFACT_BENTHOS) \\"
    template-benthos:
    template-micros:
      compose: "benthos:\n
              \   image: ${BENTHOS_ARTIFACT_NAME}\n
              \   tag: ${ARTIFACT_VERSION}\n
              \   deployRestartCount: 3\n
              \   links:\n
              \     - gateway\n
              \     - statsd-service-sidecar\n
              \   ports:\n
              \     - \"4195:4195\""
      service: "benthos:\n
              \   build:\n
              \     context: .\n
              \     dockerfile: benthos.Dockerfile\n
              \     args:\n
              \       REGISTRY: ${REGISTRY}\n
              \   image: ${IMAGE}-benthos:${TAG}"
  benthos-inbound:
    template-makefile:
      image_name: "BENTHOS_INPUT_IMAGE_NAME := $(APP_IMAGE_NAME)-benthos-input"
      hack_name: "MICROS_HACK_ARTIFACT_BENTHOS_INPUT_IMAGE_NAME := docker.atl-paas.net$(IMAGE_PATH)/$(BENTHOS_INPUT_IMAGE_NAME)"
      artifact_name: "BENTHOS_INPUT_ARTIFACT_NAME=$(MICROS_HACK_ARTIFACT_BENTHOS_INPUT_IMAGE_NAME)"
  benthos-outbound:
    template-makefile:
      image_name: "BENTHOS_OUTPUT_IMAGE_NAME := $(APP_IMAGE_NAME)-benthos-output"
      hack_name: "MICROS_HACK_ARTIFACT_BENTHOS_OUTPUT_IMAGE_NAME := docker.atl-paas.net$(IMAGE_PATH)/$(BENTHOS_OUTPUT_IMAGE_NAME)"
      artifact_name: "BENTHOS_OUTPUT_ARTIFACT_NAME=$(MICROS_HACK_ARTIFACT_BENTHOS_OUTPUT_IMAGE_NAME) \\"
  gateway:
    template-makefile:
      image_name: "Makefile Placeholder Gateway"
    template-micros:
      image_name: "Placeholder"
    template-gateway:
      image_name: "Placeholder"
```

