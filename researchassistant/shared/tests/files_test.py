import os
from researchassistant.shared.files import create_project_dir


def test_create_project_dir():
        data = {
            "project_name": "new_project"
        }
        result = create_project_dir(data)
        expected_project_dir = "./project_data/new_project"

        assert result["project_dir"] == expected_project_dir
        assert os.path.exists(expected_project_dir)

        os.rmdir(expected_project_dir)
