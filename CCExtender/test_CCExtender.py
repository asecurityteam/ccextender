#!/usr/bin/env python

import pytest
import sys
sys.path.append("/go/src/Users/aslape/python/src/github.com/CCExtender/")
# from CCExtender import CCExtender
from CCExtender.CCExtender import CCExtender
import oyaml as yaml
import os

config_path = "CCExtender/configs/typical_context_config.yaml"
config_normal = yaml.safe_load(open("CCExtender/configs/typical_context_config.yaml", 'r'))
config_large = yaml.safe_load(open("CCExtender/configs/large_context_config.yaml", 'r'))
config_small = yaml.safe_load(open("CCExtender/configs/small_context_config.yaml", 'r'))

standard_template = "template-makefile"

cc_extender = CCExtender(ccx_config = config_path, std_template = standard_template, test_mode = True)

defaults_normal = {
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

changepacks_normal = {
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
    test_ccx = cc_extender.get_standards(config_normal, defaults_normal, standard_template)
    assert test_ccx["project_namespace"] == "test team"

def test_get_standards_small():
    test_ccx = cc_extender.get_standards(config_small, defaults_normal, standard_template)
    assert test_ccx["project_name"] == "test project"

def test_get_standards_large():
    test_ccx = cc_extender.get_standards(config_large, defaults_normal, standard_template)
    assert test_ccx["project_namespace"] == "test team"

def test_get_decisions_typical():
    test_ccx = cc_extender.get_decisions(config_normal)
    assert "Makefile Placeholder Gateway" in test_ccx["template-makefile"]["image_name"]

def test_get_decisions_small():
    test_ccx = cc_extender.get_decisions(config_small)
    assert test_ccx["template-gateway"]["image_name"] == "Placeholder\n"

def test_get_decisions_large():
    test_ccx = cc_extender.get_decisions(config_large)
    assert "Makefile Placeholder Gateway" in test_ccx["template-makefile"]["image_name"]

def test_get_defaults():
    test_ccx = cc_extender.get_defaults(cc_extender.get_templates(config_normal))
    assert test_ccx["template-makefile"]["project_namespace"] == "asecurityteam"

def test_get_templates():
    test_ccx = cc_extender.get_templates(config_normal)
    assert test_ccx["template-makefile"] == "CCExtender/configs/template-makefile/"

def test_get_changes():
    test_ccx = cc_extender.get_changes(changepacks_normal, config_normal)
    assert "BENTHOS_IMAGE_NAME := $(APP_IMAGE_NAME)-benthos" in test_ccx["template-makefile"]["image_name"]

def test_load_config_yaml():
    test_ccx = cc_extender.load_config_yaml(config_path, "/go/src/mirror/")
    assert float(test_ccx["CCX_Version"]) > 0.9

def test_prompt_user_input():
    test_ccx = cc_extender.prompt_user_input("test", "2")
    assert test_ccx == "2"

def test_prompt_user_decision():
    test_ccx = cc_extender.prompt_user_decision(config_normal["decisions"]["benthos"], "benthos", "1")
    assert test_ccx == ["benthos", "gateway"] or test_ccx == ["gateway", "benthos"]

def test_interpret_decision():
    test_ccx = cc_extender.interpret_decision("1", config_normal["decisions"]["benthos"], "1")
    assert test_ccx == "benthos"

# def test_init():
#     new_ext = CCExtender(ccx_config = config_path, std_template = standard_template, test_mode=True)

def test_black_box():
    os.system("python3 -m CCExtender.CCExtender -c " + config_path + " -s " + standard_template + " -t " + "True" + " -o " + ".")
    #CCExtender(ccx_config = config_path, std_template = standard_template, test_mode = True, outdir = "")
    assert(os.path.isdir('my-new-oss-library') and os.path.isfile('my-new-oss-library/sec-my-new-oss-library.sd.yml'))

def test_clean_up():
    os.system("rm -r my-new-oss-library")