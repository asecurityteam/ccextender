#!/usr/bin/env python
'''Unit testing for ccextender module'''

import os
import oyaml as yaml
from pkg.ccextender.ccextender import CCExtender
#from ccextender import CCExtender

CONFIG_PATH = "pkg/ccextender/configs/typical_context_config.yaml"
CONFIG_NORMAL = yaml.safe_load(open("pkg/ccextender/configs/typical_context_config.yaml", 'r'))
CONFIG_LARGE = yaml.safe_load(open("pkg/ccextender/configs/large_context_config.yaml", 'r'))
CONFIG_SMALL = yaml.safe_load(open("pkg/ccextender/configs/small_context_config.yaml", 'r'))

STANDARD_TEMPLATE = "template-makefile"

CC_EXTENDER = CCExtender(ccx_config=CONFIG_PATH, std_template=STANDARD_TEMPLATE,
                         test_mode=True)

DEFAULTS_NORMAL = {
    "template-standards":
    {
        "project_name": "test project",
        "project_slug": "test_project",
        "project_description": "this is a test project",
        "notification_email": "testy_mctesterson@atlassian.com",
        "project_namespace": "test team"
    },
    "template-makefile":
    {
        "project_name": "test project",
        "project_slug": "test_project",
        "project_description": "this is a test project",
        "notification_email": "testy_mctesterson@atlassian.com",
        "project_namespace": "test team",
        "image_name": "1",
        "hack_name": "1",
        "artifact_name": "1"
    },
    "template-benthos": {},
    "template-micros":
    {
        "compose": "Compose template test",
        "service": "Service template test"
    }
}

CHANGEPACKS_NORMAL = {
    "benthos":
    {
        "template-makefile":
        {
            "test_var": "1",
            "test_var2": "2"
        },
        "template-benthos":
        {
            "test_var": "1",
            "test_var2": "2"
        }
    },
    "gateway":
    {
        "template-makefile":
        {
            "test_var": "1"
        },
        "template-benthos":
        {
            "test_var": "1",
            "test_var2": "2",
            "test_var3": "3"
        }
    }
}


def test_get_standards_typical():
    '''Testing get standards method of ccextender class'''
    test_ccx = CC_EXTENDER.get_standards(CONFIG_NORMAL, DEFAULTS_NORMAL, STANDARD_TEMPLATE)
    assert test_ccx["project_namespace"] == "test team"

def test_get_standards_small():
    '''Testing get standards method of ccextender class'''
    test_ccx = CC_EXTENDER.get_standards(CONFIG_SMALL, DEFAULTS_NORMAL, STANDARD_TEMPLATE)
    assert test_ccx["project_name"] == "test project"

def test_get_standards_large():
    '''Testing get standards method of ccextender class'''
    test_ccx = CC_EXTENDER.get_standards(CONFIG_LARGE, DEFAULTS_NORMAL, STANDARD_TEMPLATE)
    assert test_ccx["project_namespace"] == "test team"

def test_get_decisions_typical():
    '''Testing get decisions method of ccextender class'''
    test_ccx = CC_EXTENDER.get_decisions(CONFIG_NORMAL)
    assert "Makefile Placeholder Gateway" in test_ccx["template-makefile"]["image_name"]

def test_get_decisions_small():
    '''Testing get standards method of ccextender class'''
    test_ccx = CC_EXTENDER.get_decisions(CONFIG_SMALL)
    assert test_ccx["template-gateway"]["image_name"] == "Placeholder\n"

def test_get_decisions_large():
    '''Testing get standards method of ccextender class'''
    test_ccx = CC_EXTENDER.get_decisions(CONFIG_LARGE)
    assert "Makefile Placeholder Gateway" in test_ccx["template-makefile"]["image_name"]

def test_get_defaults():
    '''Testing get defaults method of ccextender class'''
    test_ccx = CC_EXTENDER.get_defaults(CC_EXTENDER.get_templates(CONFIG_NORMAL))
    assert test_ccx["template-makefile"]["project_namespace"] == "asecurityteam"

def test_get_templates():
    '''Testing get templates method of ccextender class'''
    test_ccx = CC_EXTENDER.get_templates(CONFIG_NORMAL)
    assert test_ccx["template-makefile"] == "pkg/ccextender/configs/template-makefile/"

def test_get_changes():
    '''Testing get changes method of ccextender class'''
    test_ccx = CC_EXTENDER.get_changes(CHANGEPACKS_NORMAL, CONFIG_NORMAL)
    assert "BENTHOS_IMAGE_NAME := $(APP_IMAGE_NAME)-benthos" \
        in test_ccx["template-makefile"]["image_name"]

def test_load_config_yaml():
    '''Testing load config yaml method of ccextender class'''
    test_ccx = CC_EXTENDER.load_config_yaml(CONFIG_PATH)
    assert float(test_ccx["CCX_Version"]) > 0.9

def test_prompt_user_input():
    '''Testing prompt user input method of ccextender class'''
    test_ccx = CC_EXTENDER.prompt_user_input("test", "2")
    assert test_ccx == "2"

def test_prompt_user_decision():
    '''Testing prompt user decision method of ccextender class'''
    test_ccx = CC_EXTENDER.prompt_user_decision(CONFIG_NORMAL["decisions"]["benthos"],
                                                "benthos", "1")
    assert test_ccx in (["benthos", "gateway"], ["gateway", "benthos"])

def test_interpret_decision():
    '''Testing interpret decision method of ccextender class'''
    test_ccx = CC_EXTENDER.interpret_decision("1", CONFIG_NORMAL["decisions"]["benthos"], "1")
    assert test_ccx == "benthos"

def test_black_box():
    '''Tests the ccextender application as a whole'''
    os.system("python3 -m pkg.ccextender.ccextender -c " + CONFIG_PATH + " -s " + STANDARD_TEMPLATE
              + " -t " + "True" + " -o " + ".")
    assert(os.path.isdir('my-new-oss-library')
           and os.path.isfile('my-new-oss-library/sec-my-new-oss-library.sd.yml'))

def test_clean_up():
    '''Removes leftover repository from black box test'''
    os.system("rm -r my-new-oss-library")
