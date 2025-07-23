import os
import sys
import json

from .. import Config
from ..display import print_info
from ..utils import makedirs, _get_makefile_path, handle_filename_conflict

__default_ext_tools = """<toolSet name="External Tools">
  <tool name="powermake build" showInMainMenu="false" showInEditor="false" showInProject="false" showInSearchPopup="false" disabled="false" useConsole="true" showConsoleOnStdOut="false" showConsoleOnStdErr="false" synchronizeAfterRun="true">
    <exec>
      <option name="COMMAND" value="$powermakePythonPath$" />
      <option name="PARAMETERS" value="$powermakeMakefilePath$ -rvd -o ." />
      <option name="WORKING_DIRECTORY" value="$ProjectFileDir$" />
    </exec>
  </tool>
  <tool name="powermake clean" showInMainMenu="false" showInEditor="false" showInProject="false" showInSearchPopup="false" disabled="false" useConsole="true" showConsoleOnStdOut="false" showConsoleOnStdErr="false" synchronizeAfterRun="true">
    <exec>
      <option name="COMMAND" value="$powermakePythonPath$" />
      <option name="PARAMETERS" value="$powermakeMakefilePath$ -cvd" />
      <option name="WORKING_DIRECTORY" />
    </exec>
  </tool>
</toolSet>
"""

__default_custom_targets = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="CLionExternalBuildManager">
    <target id="6bae13da-a080-408e-bb99-ebeeb53d1969" name="powermake" defaultType="TOOL">
      <configuration id="2941e637-c315-4006-a7f6-2c5597167963" name="powermake" toolchainName="Default">
        <build type="TOOL">
          <tool actionId="Tool_External Tools_powermake build" />
        </build>
        <clean type="TOOL">
          <tool actionId="Tool_External Tools_powermake clean" />
        </clean>
      </configuration>
    </target>
  </component>
</project>
"""

__default_misc = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="CompDBSettings">
    <option name="linkedExternalProjectsSettings">
      <CompDBProjectSettings>
        <option name="externalProjectPath" value="$PROJECT_DIR$" />
        <option name="modules">
          <set>
            <option value="$PROJECT_DIR$" />
          </set>
        </option>
      </CompDBProjectSettings>
    </option>
  </component>
  <component name="CompDBWorkspace" PROJECT_DIR="$PROJECT_DIR$" />
  <component name="ExternalStorageConfigurationManager" enabled="true" />
</project>
"""

__default_workspace = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="PropertiesComponent"><![CDATA[{
  "keyToString": {
    "settings.build.tools.auto.reload": "ALL"
  }
}]]></component>
  <component name="RunManager">
    <configuration name="PowerMake" type="CLionExternalRunConfiguration" factoryName="Application" REDIRECT_INPUT="false" ELEVATE="false" USE_EXTERNAL_CONSOLE="false" EMULATE_TERMINAL="false" WORKING_DIR="$PROJECT_DIR$" PASS_PARENT_ENVS_2="true" PROJECT_NAME="$powermakeTargetName$" TARGET_NAME="powermake" CONFIG_NAME="powermake" RUN_PATH="$powermakeProgram$">
      <method v="2">
        <option name="CLION.EXTERNAL.BUILD" enabled="true" />
      </method>
    </configuration>
    <configuration default="true" type="CMakeRunConfiguration" factoryName="Application" REDIRECT_INPUT="false" ELEVATE="false" USE_EXTERNAL_CONSOLE="false" EMULATE_TERMINAL="false" PASS_PARENT_ENVS_2="true">
      <method v="2">
        <option name="com.jetbrains.cidr.execution.CidrBuildBeforeRunTaskProvider$BuildBeforeRunTask" enabled="true" />
      </method>
    </configuration>
  </component>
  <component name="CompDBLocalSettings">
    <option name="availableProjects">
      <map>
        <entry>
          <key>
            <ExternalProjectPojo>
              <option name="name" value="$powermakeTargetName$" />
              <option name="path" value="$PROJECT_DIR$" />
            </ExternalProjectPojo>
          </key>
          <value>
            <list>
              <ExternalProjectPojo>
                <option name="name" value="$powermakeTargetName$" />
                <option name="path" value="$PROJECT_DIR$" />
              </ExternalProjectPojo>
            </list>
          </value>
        </entry>
      </map>
    </option>
    <option name="projectSyncType">
      <map>
        <entry key="$PROJECT_DIR$" value="RE_IMPORT" />
      </map>
    </option>
  </component>
</project>
"""

def format_xml_string(xml_str: str, powermake_program: str, target_name: str) -> str:
    xml_str = xml_str.replace("$powermakeProgram$", json.dumps(powermake_program)[1:-1])
    xml_str = xml_str.replace("$powermakePythonPath$", json.dumps(sys.executable)[1:-1])
    xml_str = xml_str.replace("$powermakeMakefilePath$", json.dumps(os.path.realpath(_get_makefile_path() or "."))[1:-1])
    xml_str = xml_str.replace("$powermakeTargetName$", json.dumps(target_name)[1:-1])
    return xml_str

def generate_idea(config: Config, idea_path: str) -> None:
    debug = config.debug
    config.set_debug(True)
    makedirs(os.path.join(idea_path, "tools"))

    ext_tools_template_path = os.path.join(config.global_config_dir, "idea_templates", "tools", "External Tools.xml")
    custom_targets_template_path = os.path.join(config.global_config_dir, "idea_templates", "customTargets.xml")
    misc_template_path = os.path.join(config.global_config_dir, "idea_templates", "misc.xml")
    workspace_template_path = os.path.join(config.global_config_dir, "idea_templates", "workspace.xml")

    if not os.path.exists(ext_tools_template_path):
        makedirs(os.path.join(config.global_config_dir, "idea_templates", "tools"))
        with open(ext_tools_template_path, "w") as file:
            file.write(__default_ext_tools)
        ext_tools_content = __default_ext_tools
    else:
        with open(ext_tools_template_path, "r") as file:
            ext_tools_content = file.read()

    if not os.path.exists(custom_targets_template_path):
        with open(custom_targets_template_path, "w") as file:
            file.write(__default_custom_targets)
        custom_targets_content = __default_custom_targets
    else:
        with open(custom_targets_template_path, "r") as file:
            custom_targets_content = file.read()

    if not os.path.exists(misc_template_path):
        with open(misc_template_path, "w") as file:
            file.write(__default_misc)
        misc_content = __default_misc
    else:
        with open(misc_template_path, "r") as file:
            misc_content = file.read()

    if not os.path.exists(workspace_template_path):
        with open(workspace_template_path, "w") as file:
            file.write(__default_workspace)
        workspace_content = __default_workspace
    else:
        with open(workspace_template_path, "r") as file:
            workspace_content = file.read()

    powermake_program = os.path.abspath(os.path.join(config.exe_build_directory, config.target_name))

    ext_tools_filepath = handle_filename_conflict(os.path.join(idea_path, "tools", "External Tools.xml"), config._args_parsed.always_overwrite)
    if ext_tools_filepath != "":
        with open(ext_tools_filepath, "w") as file:
            file.write(format_xml_string(ext_tools_content, powermake_program, config.target_name))

    custom_targets_filepath = handle_filename_conflict(os.path.join(idea_path, "customTargets.xml"), config._args_parsed.always_overwrite)
    if custom_targets_filepath != "":
        with open(custom_targets_filepath, "w") as file:
            file.write(format_xml_string(custom_targets_content, powermake_program, config.target_name))

    misc_filepath = handle_filename_conflict(os.path.join(idea_path, "misc.xml"), config._args_parsed.always_overwrite)
    if misc_filepath != "":
        with open(misc_filepath, "w") as file:
            file.write(format_xml_string(misc_content, powermake_program, config.target_name))

    workspace_filepath = handle_filename_conflict(os.path.join(idea_path, "workspace.xml"), config._args_parsed.always_overwrite)
    if workspace_filepath != "":
        with open(workspace_filepath, "w") as file:
            file.write(format_xml_string(workspace_content, powermake_program, config.target_name))

    config.set_debug(debug)


def generate_idea_if_asked(config: Config) -> bool:
    if config._args_parsed.generate_idea is not False:
        print_info("Generating .idea folder", config.verbosity)
        idea_path: str = ""
        if config._args_parsed.generate_idea is not None:
            idea_path = config._args_parsed.generate_idea
        if not idea_path.endswith(".idea") and not idea_path.endswith(".idea/") and not idea_path.endswith(".idea\\"):
            idea_path = os.path.join(idea_path, ".idea")
        generate_idea(config, idea_path)
        print_info("done", config.verbosity)
        return True
    return False