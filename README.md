<a id="markdown-CCExtender" name="CCExtender"></a>
# CCExtender -- Cookiecutter with branching builds

https://github.com/asecurityteam/ccextender

<!-- TOC -->

- [CCExtender](#CCExtender)
    - [Overview](#overview)
    - [Commands](#commands)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Configuration](#configuration)
    - [Setting up your templates](#settingupyourtemplates)
      - [Additive variable assignment](#additivevariableassignment)
    - [Hello World](#helloworld)
    - [Common Issues](#commonissues)
    - [Extending CCExtender](#extendingccextender)

<!-- /TOC -->

<a id="markdown-overview" name="overview"></a>
## Overview

CCExtender, or CCX, is a repository construction application built on top of cookiecutter (a templating program). Its primary purpose is to provide a framework for logical, branching build paths that can create customized repositories based on user decisions.

###### How CCExtender works, briefly
1. You'll create various cookiecutter templates containing the building blocks of your typical repository setup. Using a few new techniques introduced by CCExtender, your templates will be ready to receive large and complicated packs of changes (change-packs).
2. You'll write a configuration file where you define these so-called change-packs, along with the user prompts and build logic that will be used in constructing your future repos.
3. From this point on, you'll simply run CCExtender against your configuration file whenever you want to create a repository. By answering the prompts written in the configuration file, you'll guide the build of each repository to fit your needs. CCExtender will save you time by making various configuration changes automatically, while also making sure your repository only has exactly what you need.


###### What CCExtender is good for:
- Developers that regularly create new repositories with similar structure and content
- Anyone who wants to automate the creation of templatized files and folders

###### What CCExtender is bad for:
- One time repository creation. CCExtender is a way to front-load the work of creating many repositories, and won't bring much value to teams that only need one or two similar repos.

<a id="markdown-commands" name="commands"></a>
## Commands

```bash
ccextender
    help
    --ccx_config, -c <Path to configuration file>
    --std_template, -s <Path to template containing defaults for your standards> #(See #standards)
    --test_mode, -t # Activates test mode (which disables prompts for stdin)
    --outdir, -o <Path to desired repository location>
```

<a id="markdown-installation" name="installation"></a>
## Installation

#### Prequisites:

Python 3

oyaml - a python package allowing for yaml files to read as an ordered dictionary

cookiecutter - a templating application


```bash
pip3 install cookiecutter oyaml
```

```bash
pip3 install ccextender
```

<a id="markdown-usage" name="usage"></a>
## Usage

CCExtender requires a yaml configuration file and at least one cookiecutter template directory to function.

For more information on how to set up cookiecutter templates, visit: https://cookiecutter.readthedocs.io/en/latest/first_steps.html

For how to setup a configuration file, read the #Configuration section of this doc.

#### 1. Create a configuration file.

Your configuration file will contain the logic for your interactive build, directions to the templates you plan to use, and what templatized changes should be associated with your decisions.

By default, ccextender will look for a file named ccextender.yaml in your current directory, but you can direct it to read any file through the --ccx_config flag:

```bash
ccextender --ccx_config=/Users/me/Documents/myconfig.yaml
```

Your configuration file must follow the YAML format. To see how to write a CCExtender config file, see [Configuration](#Configuration).

#### 2. Run CCExtender

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

To use a specific template for the default values for your standards:
```bash
ccextender -s template-standards
```

NOTE: This isn't a path or location of the template, but merely the template's directory name. You should add the templates location in the configuration file under the "locations" section. See [Configuration](#Configuration).

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
<a id="markdown-configuration" name="configuration"></a>
## Configuration

```YAML
CCX_Version: X.X # Non-essential as of version 1.1
standard-context: # Standard variables that exist across most or all templates involved in build. This saves us the trouble of needing to re-type them for each template.
  project_name: "Example default name" # "project_name" corresponds to a variable in a cookiecutter.json file, and the right side string is the default value. Users will have the option to replace this default value for all standard-context variables.
  project_slug: "example-default-slug"
  project_namespace: "example-team"
decisions: # A series of decision blocks where the user responds to prompts with numerical choices, which then mark particular change-packs to be added into the repository.
  decision-block-one: # Decision blocks consist of a query block, followed by a list of choice blocks
    query: # query blocks contain the prompt given to the end-user and possibly some logic flags to indicate whether or not the decision-block should be run.
      prompt: "Example question asking user to pick between [1] and [2]?" # CCExtender reads YAML files as ordered dicts, so the order of each choice is preserved, thus "choice-one" corresponds to 1 and "choice-two" corresponds to 2. A response of 0 will skip the decision block, and a blank response defaults to 1 (as of version 1.11 of CCX)
    choice-one: # When a choice is selected, all change-packs under its block will be added to the new repository.
      - change-pack-A # tag corresponds to the change-pack of the same name in the change-packs block
      - change-pack-B
    choice-two:
      - change-pack-C
  decision-block-two:
    query:
      prompt: "Example question asking user to pick between [1], [2], or [3]?"
      exclude-if: # excludes this entire decision block if the user has picked choice-one in a previous decision block
        - choice-one
    2nd-choice-one:
      - change-pack-D
    2nd-choice-two:
      - change-pack-E
    2nd-choice-three:
      - change-pack-D
      - change-pack-F
  decision-block-three:
    query:
      prompt: "Would you like to pick [1]?"
      include-if: # includes the decision block only if the user has selected both the of below choices
        - 2nd-choice-three
        - choice-two
      exclude-if:
        - choice-two
      3rd-choice-one:
        - change-pack-G
  change-packs: # change packs define which templates should be added into the repository, and in some cases, what variables should be set to for those templates.
    change-pack-A:
      template-makefile: # Refers to the template-makefile listed in the locations block
        registry_link: "REGISTRY := registry.hub.docker.com" # corresponds to a variable called "registry_link" defined in the template-makefile's cookiecutter.json
        environment: "ENVIRON := dev"
      template-dockerfile:
        pip_install: "pip install cookiecutter"
    change-pack-B:
      template-dockerfile:
        pip_install: "pip install setuptools" #Since you can pick both change-pack-A and change-pack-B, which both set a different value for the same variable in template-dockerfile, how do we know which value is used? The answer is both. In the Dockerfile stored in template-dockerfile, the templatized variable {{cookiecutter.pip_install}} will be replaced with two lines of code (or more if other changepacks also set a value to pip_install). Essentially, when more than one value is set to a variable, it is appended to the current value as "\nnew value". Thus, in this case, where change-packs A and B are both used, we end up with "pip install cookiecutter\npip install setuptools" creating two lines in the place of the cookiecutter variable.
    change-pack-C:
      template-makefile:
        registry_link: "REGISTRY := privateregistry.hub.docker.com"
        environment: "ENVIRON := prod"
    change-pack-D:
      template-version:
        version: "v2"
    change-pack-E:
      template-version:
        version: "v3"
    change-pack-F:
      template-travis: # You don't need to set a variable to use a template. Here, this change pack will pull in the travis template without setting any cookiecutter variables. Note, if template-travis has variables in its cookiecutter.json that are not covered by the standard-context, you will need to include variable assignment here.
    change-pack-G:
      template-readme:
      template-license:
      template-dockerfile:
        pip_install: "pip install pylint" # adds "\npip install pylint" to current value of pip_install
  locations:
    home:
      - https://github.com/yourtemplates/ # you can reference github template repos directly
    local_home:
      - /Users/you/your-templates/ # you can also reference local directories
    template-makefile:
      - $!home$ # To save time, you can create path shortcuts (like how we wrote home and local-home) and then add them in the ordered list here. CCExtender will then go through the list and append each section to the path string. In this case, we end up with https://github.com/yourtemplates/template-makefile
      - template-makefile
    template-dockerfile:
      - $!home$
      - template-dockerfile
    template-version:
      - $!home$
      - template-version
    template-travis:
      - $!local_home$
      - my-travis-template
    template-readme:
      - $!home$
      - template-readme
    template-license:
      - https://github.com/licensing-template
    template-standards:
      - $!home$
      - template-standards
```

<a id="markdown-settingupyourtemplates" name="settingupyourtemplates"></a>
## Setting up your templates

Cookiecutter templates are fairly straightforward.

Their structure is:

```
template-example/
    cookiecutter.json
    <content to be templatized>
```

The cookiecutter.json file is where you traditionally define your template variables, along with their default values. They might look something like this:

```json
{
"greeting": "Hello World",
"recipient": "You",
"license": "MIT License"
}
```

When you'd run cookiecutter, it would prompt you to enter values for each variable, and then replace all instances of {{cookiecutter.<variable name>}} in every file within the template, before copying them into your target directory.

CCExtender works differently, though. The only values you have to manually input are variables in your standards template (usually general stuff like project name, contact email, etc.) All the variables in the rest of your templates will be set by the change-packs you've configured in your configuration file.

So let's say you run CCExtender and make a decision that triggers change-pack-A:

```YAML
change-pack-A:
  template-makefile: # Refers to the template-makefile listed in the locations block
    registry_link: "REGISTRY := registry.hub.docker.com" # corresponds to a variable called "registry_link" defined in the template-makefile's cookiecutter.json
    environment: "ENVIRON := dev"
  template-dockerfile:
    pip_install: "RUN pip install cookiecutter"
```

Change-pack-A assigns values to variables in our makefile template and our docker file template's cookiecutter.json files. Those files might look like:

template-makefile/cookiecutter.json
```json
{
  "project_name": "My New Project",
  "registry_link": "",
  "environment": "ENVIRON := test"
}
```

template-dockerfile/cookiecutter.json
```json
{
  "project_name": "My New Project",
  "pip_install": ""
}
```

Then when CCExtender creates a new repository, it uses the variable assignments from change-pack-A for their corresponding cookiecutter variables. So you can think of the variable assignments in the change-pack blocks in our ccextender.yaml file to essentially take the place of your manually entering them in a traditionally cookiecutter session.

<a id="markdown-additivevariableassignment" name="additivevariableassignment"></a>
#### Additive Variable assignment

CCExtender lets you assign multiple values to the same variable. For instance, let's look at the cookiecutter.json for the dockerfile template from earlier:

template-dockerfile/cookiecutter.json
```json
{
  "project_name": "My New Project",
  "pip_install": ""
}
```

The pip_install variable corresponds to {{cookiecutter.pip_install}} in the Dockerfile:

Dockerfile
```Dockerfile
...
COPY . somefolder/

{{cookiecutter.pip_install}}

RUN apt-get blahblahblah
...
```

Now let's say you have a configuration file with a changepack section like this:

ccextender.yaml
```YAML
change-pack-A:
  template-dockerfile:
    pip_install: "RUN pip install cookiecutter"
change-pack-B:
  template-dockerfile:
    pip_install: "RUN pip install setuptools"
change-pack-C:
  template-dockerfile:
    pip_install: "RUN pip install oyaml"
    pip_install: "RUN pip install pylint"
```

Now let's say we run CCExtender and our decisions lead to change packs A, B, and C being used. That means that pip_install is being assigned a value 4 times. After the first assignemnt, CCExtender appends each subsequent assigned value to the end of the current value string, separated by a '\n'. This results in CCExtender inserting multiple lines in the place a single value. For our example, the Dockerfile would now look like:

Dockerfile
```Dockerfile
...
COPY . somefolder/

RUN pip install cookiecutter
RUN pip install setuptools
RUN pip install oyaml
RUN pip install pylint

RUN apt-get blahblahblah
...
```

<a id="markdown-helloworld" name="helloworld"></a>
## Hello World

#### 1. Create practice templates

###### Create template directories:

```bash
mkdir templates
cd templates

mkdir -p template-project-info/{{cookiecutter.project_name}}
mkdir -p template-hello/{{cookiecutter.project_name}}
mkdir -p template-goodbye/{{cookiecutter.project_name}}
mkdir -p template-standards/{{cookiecutter.project_name}}
```

###### Create README template:

In the template-project-info/ directory, add file cookiecutter.json with the following contents:

```json
{
"project_name": "HelloWorld",
"owner": "New User",
"contact_email": "you@default.com"
}
```

Then move into the lower directory:

```bash
cd {{cookiecutter.project_name}}
```

Add file README.txt with the following contents:

```text
{{cookiecutter.project_name}} Project Documentation

This project was created by:
{{cookiecutter.owner}}

For questions about this project, please email {{cookiecutter.contact_email}}.
```

###### Create Hello World template:

In the template-hello directory, add file cookiecutter.json with the following contents:

```json
{
    "project_name": "HelloWorld",
    "contact_email": "you@default.com",
    "owner": "New User",
    "greeting": "Hello"
}
```

Then move into the lower directory:

```bash
cd {{cookiecutter.project_name}}
```

Add file hello.py with the following contents:

```python
print("{{cookiecutter.owner}} would like to say {{cookiecutter.greeting}}")
```

###### Create Goodbye template:

In the template-goodbye directory, add a file cookiecutter.json with the following content:

```json
{
    "project_name": "HelloWorld",
    "contact_email": "you@default.com",
    "owner": "New User",
    "greeting": "Goodbye"
}
```

Then move into the lower directory:

```bash
cd {{cookiecutter.project_name}}
```

Add file hello.py with the following contents:

```python
print("{{cookiecutter.owner}} would like to say {{cookiecutter.greeting}}")
```

###### Create Standards Template:

In the template-standards directory, add file cookiecutter.json with the following contents:

```json
{
"project_name": "HelloWorld",
"owner": "New User",
"contact_email": "you@default.com"
}
```

#### 2. Create your configuration file:

In your templates folder, create a file ccextender.yaml with the following content:

```yaml
CCX_Version: 1.1
standard-context:
  project_name: "HelloWorld"
  owner: "New User"
  contact_email: "you@default.com"
decisions:
  readme:
    query:
      prompt: "Would you like to [1] add project readme info?"
    yes:
      - project-info
  greeting:
    query:
      prompt: "Would you like to say [1] hello or [2] goodbye?"
      include-if:
        - yes
    hello:
      - hello-pack
    goodbye:
      - goodbye-pack
change-packs:
  hello-pack:
    template-hello:
      greeting: "Howdy"
  goodbye-pack:
    template-goodbye:
  project-info:
    template-project-info:
locations:
  home:
    - <path to your templates folder>
  template-hello:
    - $!home$
    - template-hello
  template-goodbye:
    - $!home$
    - template-goodbye
  template-project-info:
    - $!home$
    - template-project-info
  template-standards:
    - $!home$
    - template-standards
```

#### 3. Run CCExtender

Now, navigate to the directory where you saved ccextender.yaml and then type:

```bash
ccextender
```

Answer the prompts. Once you are finished, you should see a new repository has been created in your current directory. Navigate into the repo and the run:

```bash
python hello.py
```

You should see that your changes have been implemented. Try running the program a few times, and you’ll see how the build changes.

<a id="markdown-commonissues" name="commonissues"></a>
## Common Issues

###### CCExtender can't find a cookiecutter.json for a template

So this either means that the path or url pointing to your template is broken or that one of your cookiecutter templates are missing the cookiecutter.json file. Verify that you have a cookiecutter.json in all template directories, including your standard template, and then verify that your links/paths work by manually calling them with:

```bash
cookiecutter <path or link to your cookiecutter template>
```

<a id="markdown-extendingccextender" name="extendingccextender"></a>
## Extending ccextender

#### Adding new logic flags

So as of writing this, CCExtender only has two logical flags: include-if and exclude-if. But there is no limit on how many new flags can be added nor what they can do. To add a new flag, navigate to ccextender.py in pkg/ccextender and look at the class function prompt_user_decision. You should see a comment indicating the logic flag section. Right now, it looks something like this:

```Python
#Include-if flag logic
if "include-if" in query_block.keys():
      for condition in query_block["include-if"]:
          if condition not in self.past_decisions:
              print(str(condition) + " NOT in " + str(self.past_decisions))
              return list()
#Exclude-if flag logic
if "exclude-if" in query_block.keys():
    for condition in query_block["exclude-if"]:
        if condition in self.past_decisions:
            print(str(condition) + " in " + str(self.past_decisions))
            return list()
```

The only standard part your new code will need is the following:

```Python
#My-new-flag flag logic
if "my-new-flag" in query_block.keys():
    #Your flag's code here
```

For instance, let's say we want to let users configure the color of the user prompt:

```Python
#Color flag logic
if "color" in query_block.keys():
    color_choice = query_block[color]
    if color_choice == "blue":
        prompt_string = '\033[94m' + prompt_string + '\033[0m'
    else if color_choice == "green":
        prompt_string = '\033[92m' + prompt_string + '\033[0m'
```

And then we'd just add the following line to any decision block we'd like to color:

```YAML
decisions:
  readme:
    query:
      prompt: "Would you like to [1] add project readme info?"
      color: green
    yes:
      - project-info
  greeting:
    query:
      prompt: "Would you like to say [1] hello or [2] goodbye?"
      include-if:
        - yes
      color: blue
    hello:
      - hello-pack
    goodbye:
      - goodbye-pack
```
