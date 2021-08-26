import os
import pytest
import uuid
from .utility import (
    get_platform_type,
    runner_invoke,
)
from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output

pytestmark = pytest.mark.e2e

output = Output()
envvars = EnvVars(output)
test_solution_shared_lib_dir = os.path.join(os.getcwd(), "tests", "assets", "test_solution_shared_lib")


def test_add_tags():
    # Arrange
    os.chdir(test_solution_shared_lib_dir)

    # Act
    result = runner_invoke(['tag', '--tags', '{"environment":"dev","building":"9"}'])

    # Assert
    assert 'TAG UPDATE COMPLETE' in result.output
    assert '{"environment":"dev","building":"9"}' in result.output
    assert 'ERROR' not in result.output


@pytest.mark.parametrize(
    "tags",
    [
        "tags.environment='dev'",
        "dev"
    ]
)
def test_add_tags_wrong_format(tags):
    # Arrange
    os.chdir(test_solution_shared_lib_dir)

    # Act
    result = runner_invoke(['tag', '--tags', tags])

    # Assert
    assert f"ERROR: Failed to add tag: '{tags}' to device" in result.output


def test_deployment_and_add_tags():
    # Arrange
    os.chdir(test_solution_shared_lib_dir)
    deployment_name = f'test-{uuid.uuid4()}'

    # Act
    temp = "deployment.template.json"
    result = runner_invoke(['build', '--push', '-f', temp, '-P', get_platform_type()])
    result = runner_invoke(['tag', '--tags', '{"environment":"dev"}',
                            '-d',
                            '-f', f'config/{temp.replace("template", get_platform_type())}',
                            '-n', deployment_name,
                            '-p', '10',
                            '-t', "tags.environment='dev'"])
    # Assert
    assert 'DEPLOYMENT COMPLETE' in result.output
    assert 'TAG UPDATE COMPLETE' in result.output
    assert '{"environment":"dev"}' in result.output
    assert 'ERROR' not in result.output


def test_error_creating_deployment_and_add_tags():
    # Arrange
    os.chdir(test_solution_shared_lib_dir)
    deployment_name = f'test-{uuid.uuid4()}'

    # Act
    temp = "deployment.template.json"
    result = runner_invoke(['build', '--push', '-f', temp, '-P', get_platform_type()])
    result = runner_invoke(['tag', '--tags', '{"environment":"dev"}',
                            '-d',
                            '-f', f'config/{temp.replace("template", get_platform_type())}',
                            '-n', deployment_name,
                            '-t', "tags.environment='dev'"])
    # Assert
    assert 'DEPLOYMENT COMPLETE' in result.output
    assert 'TAG UPDATE COMPLETE' not in result.output
    assert '{"environment":"dev"}' not in result.output


def test_error_missing_tag():
    # Arrange
    os.chdir(test_solution_shared_lib_dir)

    # Act
    with pytest.raises(Exception) as context:
        runner_invoke(['tag', '--tags'])

    # Assert
    assert "Error: Option '--tags' requires an argument." in str(context)


def test_invalid_tag():
    # Arrange
    os.chdir(test_solution_shared_lib_dir)

    # Act
    result = runner_invoke(['tag', '--tags', "invalid_tag"])

    # Assert
    assert "ERROR: Failed to add tag: 'invalid_tag' to device" in result.output
