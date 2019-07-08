from cookiecutter import generate
from cookiecutter.main import cookiecutter
import os
import oyaml as yaml
from collections import OrderedDict
import sys
import argparse

class CCExtender:

    test_mode = False

    def __init__(self, ccx_config = "CCExtender.yaml", std_template = "template-standards", test_mode = None, outdir = "/go/src/mirror/"):

        # Output format
        # {
        #     standard:
        #     {
        #         variable: value
        #     }
        #     template1:
        #     {
        #         variable: value,
        #         variable: value
        #     }
        # }
        if test_mode != None:
            self.test_mode = True
            print("Test mode is on")
            #return

        output = dict()

        #config is a dictionary of CCExtender.yaml (or whatever config file is used)
        config = self.load_config_yaml(ccx_config, outdir)
        #templates is a dictionary pairing template names with their paths (or links)
        templates = self.get_templates(config)
        #defaults is a dictionary of default variable values, categorized by template
        defaults = self.get_defaults(templates)
        #standards is a dictionary of standard values that exist in all our repositories
        #Essentially, these values will be reused for each template involved in the build
        standards = self.get_standards(config, defaults, std_template)
        output.update(self.get_decisions(config))
        #print output
        for template in output:
            bundled = output[template].copy()
            bundled.update(standards)
            #print bundled
            cookiecutter(templates[template], no_input = True, extra_context = bundled, overwrite_if_exists=True, output_dir = outdir)

        return

    def __main__(self):
        return

    def get_standards(self, config, defaults, standard_model_template):
        # Output:
        # standard-context:
        # {
        #     variable:value
        # }

        standards = dict()
        #standards["standard-context"] = dict()

        for variable in config["standard-context"]:
            # print variable
            # print defaults
            #standards["standard-context"].update({variable: self.prompt_user_input(variable, defaults[self.standard_model_template][variable])})
            if variable in defaults[standard_model_template].keys():
                standards[variable] = self.prompt_user_input(variable, defaults[standard_model_template][variable])

        #print standards
        return standards

    def get_decisions(self, config):
        # Output:
        # template 1:
        # {
        #     variable: value
        # }

        changepacks = list()

        for decision_block in config["decisions"]:
            change_list = self.prompt_user_decision(config["decisions"][decision_block], decision_block, "1")

            for changepack in change_list:
                changepacks.append(changepack)
            #changepacks.append(self.prompt_user_decision(config["decisions"][decision_block], decision_block, 1))

        changes = self.get_changes(changepacks, config)

        return changes

    def get_defaults(self, templates):
        # Output:
        # template 1:
        # {
        #     variable: default value
        # }

        defaults = dict()



        for template in templates:
            if "template" in template:
                defaults[template] = generate.generate_context(templates[template] + "cookiecutter.json")["cookiecutter"]

        return defaults

    def get_templates(self, config):

        #Output:
        # template1:
        # {
        #     path: path...
        # }

        templates = dict()

        for template in config["locations"]:
            templates[template] = ""
            for path in config["locations"][template]:
                templates[template] += path

        for template in templates:
            path = templates[template]
            segmented = path.split("$")
            for part in segmented:
                if "!" in part:
                    templates[template] = path.replace("$" + part + "$", templates[part.replace("!", "")])
        return templates

    def get_changes(self, changepacks, config):
        #Output
        # template1:
        #     {
        #         variable: value,
        #         variable: value
        #     }
        #Change packs format
        # change pack 1:
        # {
        #     template 1:
        #     {
        #         variable: value
        #         variable: value
        #     }
        #     template 2:
        #     ...
        # }

        changes = dict()
        # print changepacks
        for pack in changepacks:
            # print config["change-packs"]
            # print pack
            #for template in config["change-packs"][pack[0]]:
            for template in config["change-packs"][pack]:
                if template not in changes.keys():
                    changes[template] = dict()
                #print pack
                #print pack[0]

                #for variable in config["change-packs"][pack[0]][template]:
                # for minipack in pack:
                if config["change-packs"][pack][template] != None:
                    for variable in config["change-packs"][pack][template]:
                        #print config["change-packs"][pack[0]]
                        if variable in changes[template].keys():
                            value = config["change-packs"][pack][template][variable]
                            changes[template][variable] += value + "\n"
                        else:
                            changes[template][variable] = ""
                            value = config["change-packs"][pack][template][variable]
                            changes[template][variable] += value + "\n"

        return changes

    def load_config_yaml(self, ccx_config, shared_volume):
        config_file = OrderedDict()
        if self.test_mode:
            config_file = open(ccx_config, 'r')
        else:
            config_file = open(shared_volume + ccx_config, 'r')
        return yaml.safe_load(config_file)

    def prompt_user_input(self, variable, default):

        print("[return] for default: [" + default + "]")
        if self.test_mode:
            response = default
        else:
            response = input("[" + variable + "]: ")

        if response == "":
            return default
        else:
            return response


    def prompt_user_decision(self, decision_block, block_name, default):
        #Output format: A list of change packs
        #Decision Block format
        # block name:
        # {
        #     prompt: "<query asking for user decision>",
        #     option 1:
        #     {
        #         - change pack
        #         - change pack
        #     }
        #     option 2:
        #     {
        #         - change pack
        #     }
        #     ...
        # }

        prompt_string = decision_block["prompt"]

        i = 0
        for choice in decision_block:
            if choice != "prompt":
                prompt_string.replace("\%" + str(i), "[" + str(i) + "] " + choice)
            i += 1

        print("\n[" + block_name + "]")
        print(prompt_string)
        print("[return] for default: [" + str(default) + "]")
        if self.test_mode:
            decision = self.interpret_decision(default, decision_block, default)
        else:
            decision = self.interpret_decision(input("[0] to skip: "), decision_block, default)

        response = []

        if decision != "prompt":
            for pack in decision_block[decision]:
                response.append(pack)

        return response

    def interpret_decision(self, decision, decision_block, default):
        if decision == "":
            decision = str(default)
        # print decision_block
        i = 0
        for option in decision_block:
            if str(i) == decision:
                decision = option
                #print "Deciding on changepack: " + decision
            i += 1

        return decision

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--ccx_config', '-c', help="path to CCExtender configuration file", type=str)
    parser.add_argument('--std_template', '-s', help="path to cookiecutter template directory from which we will base our standard defaults")
    parser.add_argument('--test_mode', '-t', help="disables user input in favor of defaults for testing purposes")
    parser.add_argument('--outdir', '-o', help="path that CCExtender should write to")

    args = vars(parser.parse_args())

    argdict = dict()

    for arg in args:
        if args[arg] != None:
            argdict[arg] = args[arg]

    CCExtender(**argdict)