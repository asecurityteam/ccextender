#!/usr/bin/env python

import pytest
import sys
sys.path.append("/go/src/Users/aslape/python/src/github.com/CCExtender/")
#from CCExtender import CCExtender
from CCExtender.CCExtender import CCExtender
import oyaml as yaml

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
    cc_extender.get_standards(config_normal, defaults_normal, standard_template)

def test_get_standards_small():
    cc_extender.get_standards(config_small, defaults_normal, standard_template)

def test_get_standards_large():
    cc_extender.get_standards(config_large, defaults_normal, standard_template)

def test_get_decisions_typical():
    cc_extender.get_decisions(config_normal)

def test_get_decisions_small():
    cc_extender.get_decisions(config_small)

def test_get_decisions_large():
    cc_extender.get_decisions(config_large)

def test_get_defaults():
    cc_extender.get_defaults(cc_extender.get_templates(config_normal))

def test_get_templates():
    cc_extender.get_templates(config_normal)

def test_get_changes():
    cc_extender.get_changes(changepacks_normal, config_normal)

def test_load_config_yaml():
    cc_extender.load_config_yaml(config_path)

def test_prompt_user_input():
    cc_extender.prompt_user_input("test", "2")

def test_prompt_user_decision():
    cc_extender.prompt_user_decision(config_normal["decisions"]["benthos"], "benthos", "1")

def test_interpret_decision():
    cc_extender.interpret_decision("1", config_normal["decisions"]["benthos"], "1")

def test_init():
    new_ext = CCExtender(ccx_config = config_path, std_template = standard_template, test_mode=True)
