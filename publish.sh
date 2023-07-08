set -e  # if any step fails, kill the entire script and warn the user something went wrong

# get VERSION from args --version=
VERSION=${1/--version=/}

export TWINE_USERNAME=${2/--username=/}
export TWINE_PASSWORD=${3/--password=/}

# in setup.py, replace the line '\tversion=...' with '\tversion={VERSION}'
sed -i.bak "s/version=.*/version='${VERSION}',/" setup.py

# remove setup.py.bak
rm "setup.py.bak"

# Read researchassistant/__init__.py, find the line that starts with __version__ and replace with '__version__ = "${VERSION}"'
sed -i.bak "s/__version__.*/__version__ = \"${VERSION}\"/" researchassistant/__init__.py
rm researchassistant/__init__.py.bak

# Check if these dependencies are installed, and install them if they aren't
pip install twine || echo "Failed to install twine"
pip install wheel || echo "Failed to install wheel"

# Make sure these work, and stop the script if they error
# Run setup checks and build
python setup.py check || { echo "Setup check failed"; exit 1; }
python setup.py sdist || { echo "Source distribution build failed"; exit 1; }
python setup.py bdist_wheel --universal || { echo "Wheel build failed"; exit 1; }

# Make sure these work, and stop the script if they error
# Upload to test repo
twine upload dist/researchassistant-${VERSION}.tar.gz --repository-url https://test.pypi.org/legacy/ || { echo "Upload to test repo failed"; exit 1; }
pip install --index-url https://test.pypi.org/simple/ researchassistant --user || { echo "Installation from test repo failed"; exit 1; }

# Final upload
twine upload dist/researchassistant-${VERSION}.tar.gz || { echo "Final upload failed"; exit 1; }
pip install researchassistant --user || { echo "Installation of researchassistant failed"; exit 1; }

git add researchassistant/__init__.py
git add setup.py
git commit -m "Updated to ${VERSION} and published"
git push origin main

# Let the user know that everything completed successfully
echo "Script completed successfully"
