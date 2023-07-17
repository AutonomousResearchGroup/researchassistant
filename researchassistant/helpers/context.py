from pathlib import Path

from researchassistant.helpers.files import (
    count_files,
    file_tree_to_dict,
    file_tree_to_string,
    get_python_files,
    zip_python_files,
)
from researchassistant.helpers.code import run_code, test_code
from researchassistant.helpers.validation import validate_file


def get_file_count(context):
    project_dir = context["project_dir"]
    context["file_count"] = count_files(project_dir)
    return context


def read_and_format_code(context):
    # Read the contents of all python files and create a list of dicts
    project_files_str = "Project Files:\n"

    main_success = context["main_success"]
    main_error = context["main_error"]

    for project_dict in context["project_code"]:
        rel_path = project_dict["rel_path"]
        file_path = project_dict["file_path"]
        content = project_dict["content"]
        validation_success = project_dict["validation_success"]
        validation_error = project_dict["validation_error"]
        test_success = project_dict.get("test_success", None)
        test_error = project_dict.get("test_error", None)

        # adding file content to the string with line numbers
        project_files_str += "\n================================================================================n"
        project_files_str += "File: {}\nPath: {}\n".format(str(rel_path), file_path)
        if "main.py" in str(rel_path):
            project_files_str += "(Project Entrypoint)\n"
            project_files_str += "Run Success: {}\n".format(main_success)
            if main_success is False:
                project_files_str += "Run Error: {}\n".format(main_error)
        project_files_str += "Validated: {}\n".format(validation_success)
        if validation_success is False:
            project_files_str += "Validation Error: {}\n".format(validation_error)
        if test_success is not None:
            project_files_str += "Tested: {}\n".format(test_success)
        if test_success is False:
            project_files_str += "Pytest Error: {}\n".format(test_error)
        project_files_str += "\n------------------------------------- CODE -------------------------------------n"
        for i, line in enumerate(content):
            project_files_str += "[{}] {}".format(i + 1, line)
        project_files_str += "\n================================================================================n"

    context["project_code_formatted"] = project_files_str
    return context


def collect_files(context):
    project_dir = context["project_dir"]
    # create a file tree dict of all files
    context["filetree"] = file_tree_to_dict(project_dir)

    # format file tree to string
    context["filetree_formatted"] = file_tree_to_string(project_dir)

    # Create an array of paths to all python files
    context["python_files"] = get_python_files(project_dir)

    project_code = []

    for file_path in context["python_files"]:
        with open(file_path, "r") as file:
            content = file.readlines()
            rel_path = Path(file_path).relative_to(project_dir)

            file_dict = {
                "relative_path": str(rel_path),
                "absolute_path": file_path,
                "content": content,
            }
            project_code.append(file_dict)
    context["project_code"] = project_code

    return context


def validate_files(context):
    project_code = context["project_code"]
    for file_dict in project_code:
        file_path = file_dict["absolute_path"]
        validation = validate_file(file_path)
        file_dict["validation_success"] = validation["success"]
        file_dict["validation_error"] = validation["error"]
    context["project_code"] = project_code
    return context


def run_tests(context):
    # get python files which don't contain test in their name

    # if not, error
    # call pytest on each file
    # no tests? error
    # tests failed? error
    # tests passed? success

    project_code = context["project_code"]

    project_code_notests = []
    project_code_tests = []
    # get python_files which also have test in the name
    for file_dict in project_code:
        file_path = file_dict["absolute_path"]
        if "test" in file_path:
            project_code_tests.append(file_dict)
        else:
            project_code_notests.append(file_dict)

    for file_dict in project_code_tests:
        file_path = file_dict["absolute_path"]
        test = test_code(file_path)
        file_dict["test_success"] = test["success"]
        file_dict["test_error"] = test["error"]
        file_dict["test_output"] = test["output"]

    context["project_code"] = project_code_notests + project_code_tests
    return context


def run_main(context):
    project_code = context["project_code"]
    # get entry from project code where the relative path includes main.py
    main_file = None
    for file_dict in project_code:
        if "main.py" in file_dict["relative_path"]:
            main_file = file_dict

    result = run_code(main_file["absolute_path"])

    context["main_success"] = result["success"]
    if result["success"] is False:
        context["main_error"] = result["error"]
    context["main_output"] = result["output"]
    return context


def backup_project(context):
    project_dir = context["project_dir"]
    project_name = context["project_name"]
    epoch = context["epoch"]
    context["backup"] = zip_python_files(project_dir, project_name, epoch)
    return context