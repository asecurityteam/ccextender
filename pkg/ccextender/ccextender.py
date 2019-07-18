'''A module building off of the cookiecutter templating application to create logical builds with
branching options and the ability to compose many different templates into one repository building
system.'''

from collections import OrderedDict
import argparse
from cookiecutter.main import cookiecutter
import oyaml as yaml

class CCExtender:
    '''CCExtender reads in a configuration file (ccx_config) for its build information, and then
    prompts the user for decisions about how they wish the build to proceed.'''

    test_mode = False
    past_decisions = list()

    def __init__(self, ccx_config="ccextender.yaml", std_template="template-standards",
                 test_mode=None, outdir="."):
        '''Output: A templatized repository'''

        # Test mode forces CCExtender not to read stdin, instead only using
        # default values for template variables
        if test_mode is not None:
            self.test_mode = True
            print("Test mode is on")

        output = dict()

        # config is a dictionary of ccextender.yaml (or whatever config file is used)
        config = self.load_config_yaml(ccx_config)
        # templates is a dictionary pairing template names with their paths (or links)
        templates = self.get_templates(config)
        # defaults is a dictionary of default variable values, categorized by template
        defaults = self.get_defaults(std_template, config)
        # standards is a dictionary of standard values that exist in all our repositories
        # Essentially, these values will be reused for each template involved in the build
        standards = self.get_standards(config, defaults, std_template)
        output.update(self.get_decisions(config))

        # After getting all of our changes, we run through each cookiecutter template and write
        # its contents into the target directory
        for template in output:
            bundled = output[template].copy()
            bundled.update(standards)
            cookiecutter(templates[template], no_input=True, extra_context=bundled,
                         overwrite_if_exists=True, output_dir=outdir)

    def get_standards(self, config, defaults, standard_model_template):
        '''
        Prompts user to set values for the variables in our standards template
        Output:
            standard-context:
            {
                variable:value
            }
        '''

        standards = dict()

        # Prompts the user for input for each standard variable in the standard-context block
        for variable in config["standard-context"]:
            if variable in defaults[standard_model_template].keys():
                standards[variable] = \
                    self.prompt_user_input(variable,
                                           defaults[standard_model_template][variable])

        return standards

    def get_decisions(self, config):
        '''
        Reads through all the decision blocks in the config file, gets user input,
        and then tracks change-packs that correspond to the user's choices.
        Output:
            template 1:
            {
                variable: value
            }
        '''

        changepacks = list()

        for decision_block in config["decisions"]:
            change_list = self.prompt_user_decision(config["decisions"][decision_block],
                                                    decision_block, "1")

            for changepack in change_list:
                changepacks.append(changepack)

        changes = self.get_changes(changepacks, config)

        return changes

    def get_defaults(self, std_template, config):
        '''
        Grabs default values from our standard-context in our config
        Output:
            template 1:
            {
                variable: default value
            }
        '''

        defaults = dict()
        defaults[std_template] = dict()

        for variable in config["standard-context"]:
            defaults[std_template][variable] = config["standard-context"][variable]

        return defaults

    def get_templates(self, config):
        '''
        Constructs paths or url links to our templates so we can pull them during
        repo construction
        Output:
            template1:
            {
                path: path...
            }
        '''

        templates = dict()

        # Turns the list of path sections for each template into a full path
        for template in config["locations"]:
            templates[template] = ""
            for path in config["locations"][template]:
                templates[template] += path

        # Searches for shortcuts like $!home$ and replaces them with their corresponding path
        for template in templates:
            path = templates[template]
            segmented = path.split("$")
            for part in segmented:
                if "!" in part:
                    templates[template] = path.replace("$" + part + "$",
                                                       templates[part.replace("!", "")])
        return templates

    def get_changes(self, changepacks, config):
        '''
        Takes changepack names that were selected by the user and assigns their changes to
        their target templates in preparation for creating the new repo.
        Output
        template1:
            {
                variable: value,
                variable: value
            }
        '''

        changes = dict()
        for pack in changepacks:
            for template in config["change-packs"][pack]:
                if template not in changes.keys():
                    changes[template] = dict()
                if config["change-packs"][pack][template] is not None:
                    for variable in config["change-packs"][pack][template]:
                        if variable in changes[template].keys():
                            value = config["change-packs"][pack][template][variable]
                            changes[template][variable] += value + "\n"
                        else:
                            changes[template][variable] = ""
                            value = config["change-packs"][pack][template][variable]
                            changes[template][variable] += value + "\n"

        return changes

    def load_config_yaml(self, ccx_config):
        '''Loads in the configuration yaml as an ordered dictionary'''
        config_file = OrderedDict()
        config_file = open(ccx_config, 'r')
        return yaml.safe_load(config_file)

    def prompt_user_input(self, variable, default):
        '''Prompts a user for input via stdin'''

        #### User Interface ####

        print("[return] for default: [" + default + "]")
        if self.test_mode:
            response = default
        else:
            response = input("[" + variable + "]: ")

        ####

        if response == "":
            return default
        else:
            return response


    def prompt_user_decision(self, decision_block, block_name, default):
        '''
        Prompts a user to make a numeric choice corresponding to an option

        Output format: A list of change packs
        Decision Block format
        block name:
        {
            query:
            {
                prompt: "<query asking for user decision>",
                include-if: <option from previous query
            }
            option 1:
            {
                - change pack
                - change pack
            }
            option 2:
            {
                - change pack
            }
            ...
        }
        '''

        query_block = decision_block["query"]

        prompt_string = query_block["prompt"]

        #### Logic Flags ####

        if "include-if" in query_block.keys():
            for condition in query_block["include-if"]:
                if condition not in self.past_decisions:
                    print(str(condition) + " NOT in " + str(self.past_decisions))
                    return list()
        if "exclude-if" in query_block.keys():
            for condition in query_block["exclude-if"]:
                if condition in self.past_decisions:
                    print(str(condition) + " in " + str(self.past_decisions))
                    return list()

        ####

        #### User Interface ####

        print("\n[" + block_name + "]")
        print(prompt_string)
        print("[return] for default: [" + str(default) + "]")
        if self.test_mode:
            decision = self.interpret_decision(default, decision_block, default)
        else:
            decision = self.interpret_decision(input("[0] to skip: "), decision_block, default)

        ####

        response = []

        # Grabs change-packs listed under user's decision and adds them to a list for repo
        # construction

        if decision != "query":
            self.past_decisions.append(decision)
            for pack in decision_block[decision]:
                response.append(pack)

        return response

    def interpret_decision(self, decision, decision_block, default):
        '''Translates user decision into a changepack option'''
        if decision == "":
            decision = str(default)
        i = 0
        for option in decision_block:
            if str(i) == decision:
                decision = option
            i += 1

        return decision

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()

    PARSER.add_argument('--ccx_config', '-c', help="path to ccextender configuration file",
                        type=str)
    PARSER.add_argument('--std_template', '-s',
                        help="path to cookiecutter template containing standard variables")
    PARSER.add_argument('--test_mode', '-t',
                        help="disables user input in favor of defaults for testing purposes")
    PARSER.add_argument('--outdir', '-o', help="path that ccextender should write to")

    ARGS = vars(PARSER.parse_args())

    ARGDICT = dict()

    for arg in ARGS:
        if ARGS[arg] is not None:
            ARGDICT[arg] = ARGS[arg]

    CCExtender(**ARGDICT)
