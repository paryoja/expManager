sudo pip install virtualenv
sudo pip install virtualenvwrapper
mkdir ~/.virtualenvs

echo export WORKON_HOME=$HOME/.virtualenvs >> ~/.bashrc
echo source /usr/local/bin/virtualenvwrapper.sh >> ~/.bashrc

source ~/.bashrc

mkvirtualenv --python=`which python3` django
